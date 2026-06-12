#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import re

from django.conf import settings
from django.contrib import auth

from keystoneauth1 import access
from keystoneauth1 import exceptions as keystone_exceptions
from keystoneauth1 import token_endpoint

from openstack_auth import exceptions as oa_exceptions
from openstack_auth import utils as auth_utils

from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import permissions

from nectar_dashboard.rcallocation import models


ACCESS_RULES_VERSION = '1.0'


def validate_token(token, remote_addr):
    """Validate a Keystone token, declaring access rules support.

    Unlike openstack_auth's validate_token, this sends the
    OpenStack-Identity-Access-Rules header, without which Keystone
    refuses to validate tokens issued from application credentials
    that have access rules. Sending the header obliges us to enforce
    the rules ourselves (see check_access_rules).
    """
    auth_url = settings.OPENSTACK_KEYSTONE_URL
    token_auth = token_endpoint.Token(endpoint=auth_url, token=token)
    sess = auth_utils.get_session(auth=token_auth, original_ip=remote_addr)
    client = auth_utils.get_keystone_client().Client(
        session=sess, debug=settings.DEBUG
    )
    try:
        token_data = client.tokens.get_token_data(
            token, access_rules_support=ACCESS_RULES_VERSION
        )
        return access.AccessInfoV3(token_data, token)
    except keystone_exceptions.ClientException:
        raise oa_exceptions.KeystoneAuthException('Token validation failed')


def path_matches(request_path, path_pattern):
    # Ported from keystonemiddleware so access rules match the same
    # way here as on other OpenStack services. The fnmatch module
    # doesn't provide the ability to match * versus **, so convert
    # to regex.
    token_regex = (
        r'(?P<tag>{[^}]*})|'  # {tag}
        r'(?P<wild>\*(?=$|[^\*]))|'  # *
        r'(?P<rec_wild>\*\*)|'  # **
        r'(?P<literal>[^{}\*])'  # anything else
    )
    path_regex = ''
    for match in re.finditer(token_regex, path_pattern):
        token = match.groupdict()
        if token['tag'] or token['wild']:
            path_regex += r'[^\/]+'
        if token['rec_wild']:
            path_regex += '.*'
        if token['literal']:
            path_regex += token['literal']
    path_regex = rf'^{path_regex}$'
    return re.match(path_regex, request_path) is not None


def check_access_rules(request, auth_ref):
    """Enforce application credential access rules, if any.

    Allows the request if the token carries no access rules, or if at
    least one rule matches the request's service, method and path.
    Matching follows keystonemiddleware semantics: '*' matches a
    single path segment, '**' matches any remainder.
    """
    access_rules = auth_ref.application_credential_access_rules
    if access_rules is None:
        return True
    for rule in access_rules:
        if (
            rule.get('service') == settings.ALLOCATION_API_SERVICE_TYPE
            and rule.get('method') == request.method
            and path_matches(request.path, rule.get('path', ''))
        ):
            return True
    return False


class KeystoneAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_X_AUTH_TOKEN')
        remote_addr = request.environ.get('REMOTE_ADDR', '')

        if not token:
            return None

        try:
            auth_ref = validate_token(token, remote_addr)
            if not check_access_rules(request, auth_ref):
                raise exceptions.AuthenticationFailed()
            user = auth.authenticate(
                request=request,
                auth_url=None,
                auth_ref=auth_ref,
                token=auth_ref.auth_token,
                project_id=auth_ref.project_id,
            )
        except oa_exceptions.KeystoneAuthException:
            raise exceptions.AuthenticationFailed()

        if user is None:
            raise exceptions.AuthenticationFailed()

        # NOTE: deliberately no auth.login() here.  Token authentication is
        # stateless, and logging the user in hands the API client a Django
        # session cookie.  Clients built on keystoneauth keep cookies for the
        # life of the process and would then be authenticated by that session
        # rather than by the token they send, which leaves them silently
        # unauthenticated once the token held in the session expires.  It
        # also means a token's access rules are enforced on every request,
        # rather than being bypassed by a session not bound to them.
        request.user = user
        return (user, None)


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        # An openstack_auth user stays 'active' once its keystone token has
        # expired, so DRF would accept the stale session and hand back a user
        # whose is_authenticated is False.  Views branch on is_authenticated,
        # so the request is silently treated as anonymous, and the other
        # authenticators never get a turn.  Ignore the stale session instead.
        user, _auth = result
        if not user.is_authenticated:
            return None

        return result


class Permission(permissions.BasePermission):
    message = 'Permission denied or allocation in wrong state.'
    roles = []
    states = []
    invalid_states = []

    def has_role(self, user, required):
        if user.is_authenticated:
            roles = set([role['name'].lower() for role in user.roles])
            required = set(required)
            if required & roles:
                return True
        return False

    def has_permission(self, request, view):
        if not self.roles:
            return True
        return self.has_role(request.user, self.roles)

    def has_object_permission(self, request, view, obj):
        if self.states:
            allocation = self.get_allocation(obj)
            return allocation and allocation.status in self.states
        elif self.invalid_states:
            allocation = self.get_allocation(obj)
            return allocation and allocation.status not in self.invalid_states
        else:
            return True

    def is_admin(self, request):
        return self.has_role(
            request.user, settings.ALLOCATION_GLOBAL_ADMIN_ROLES
        )

    def get_allocation(self, obj):
        if hasattr(obj, 'created_by'):
            allocation = obj
        elif hasattr(obj, 'allocation'):
            allocation = obj.allocation
        elif hasattr(obj, 'group'):  # quota object
            allocation = obj.group.allocation
        else:
            allocation = None
        return allocation


class IsAdmin(Permission):
    """Global permission check for admins role"""

    roles = settings.ALLOCATION_GLOBAL_ADMIN_ROLES


class ApproverOrOwner(Permission):
    roles = settings.ALLOCATION_APPROVER_ROLES

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if self.is_admin(request):
            return True

        owner = False

        allocation = self.get_allocation(obj)
        if allocation and allocation.contact_email == request.user.username:
            owner = True

        if owner or self.has_role(request.user, self.roles):
            return True
        return False


class ReadOrAdmin(Permission):
    roles = settings.ALLOCATION_GLOBAL_ADMIN_ROLES

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class ModifyPermission(Permission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if getattr(obj, 'parent_request', None):
            return False
        if self.is_admin(request):
            return True

        return super().has_object_permission(request, view, obj)


class CanApprove(ModifyPermission):
    roles = settings.ALLOCATION_APPROVER_ROLES
    states = [
        models.AllocationRequest.SUBMITTED,
        models.AllocationRequest.UPDATE_PENDING,
    ]


class CanDelete(ModifyPermission):
    roles = settings.ALLOCATION_GLOBAL_ADMIN_ROLES


class CanUpdate(ModifyPermission):
    states = [
        models.AllocationRequest.SUBMITTED,
        models.AllocationRequest.UPDATE_PENDING,
    ]


class CanAmend(ModifyPermission):
    states = [
        models.AllocationRequest.APPROVED,
        models.AllocationRequest.DECLINED,
    ]


class IsAdminOrApprover(Permission):
    roles = (
        settings.ALLOCATION_GLOBAL_ADMIN_ROLES
        + settings.ALLOCATION_APPROVER_ROLES
    )
