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

from django.conf import settings
from django.contrib import auth

from openstack_auth import user as auth_user

from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import permissions

from nectar_dashboard.rcallocation import models


class KeystoneAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        token = request.META.get('HTTP_X_AUTH_TOKEN')
        project_id = request.META.get('HTTP_X_PROJECT_ID')
        if not token:
            return None
        try:
            request.user = auth.authenticate(request=request,
                                             token=token,
                                             project_id=project_id)
        except exceptions.KeystoneAuthException:
            raise exceptions.AuthenticationFailed()

        auth_user.set_session_from_user(request, request.user)
        auth.login(request, request.user)
        return (request.user, None)


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class Permission(permissions.BasePermission):

    message = 'Permission denied or allocation in wrong state.'
    roles = []
    states = []

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
        if not self.states:
            return True

        allocation = self.get_allocation(obj)
        if allocation and allocation.status in self.states:
            return True
        return False

    def is_admin(self, request):
        return self.has_role(request.user,
                             settings.ALLOCATION_GLOBAL_ADMIN_ROLES)

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
    """
    Global permission check for admins role
    """
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
        if allocation and \
           allocation.contact_email == request.user.username:
            owner = True

        if owner or self.has_role(request.user, self.roles):
            return True
        return False


class ReadOrAdmin(Permission):

    roles = settings.ALLOCATION_GLOBAL_ADMIN_ROLES

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super(ReadOrAdmin, self).has_permission(request, view)


class ModifyPermission(Permission):

    def has_object_permission(self, request, view, obj):
        if self.is_admin(request):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True

        return super(ModifyPermission, self).has_object_permission(request,
                                                                   view, obj)


class CanApprove(ModifyPermission):
    roles = settings.ALLOCATION_APPROVER_ROLES
    states = [models.AllocationRequest.SUBMITTED,
              models.AllocationRequest.UPDATE_PENDING]


class CanDelete(ModifyPermission):
    roles = settings.ALLOCATION_GLOBAL_ADMIN_ROLES


class CanUpdate(ModifyPermission):
    states = [models.AllocationRequest.SUBMITTED,
              models.AllocationRequest.UPDATE_PENDING]


class CanAmend(ModifyPermission):
    states = [models.AllocationRequest.APPROVED,
              models.AllocationRequest.DECLINED]
