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


def has_roles(user, project_roles, system_roles):
    """Check a user's token roles against the lists for its token scope.

    A system-scoped keystone token is checked against system_roles;
    any other (project-scoped) token against project_roles.  The two
    lists are kept separate because keystone's role inference hands
    every project user implied roles like 'reader', which must not
    grant API-wide access when carried by a project-scoped token.
    """
    if not user.is_authenticated:
        return False
    if getattr(user, 'system_scoped', False):
        required = {role.lower() for role in system_roles}
    else:
        required = {role.lower() for role in project_roles}
    roles = {role['name'].lower() for role in user.roles}
    return bool(required & roles)


def is_read_admin(user):
    return has_roles(
        user,
        settings.ALLOCATION_GLOBAL_ADMIN_ROLES
        + settings.ALLOCATION_APPROVER_ROLES
        + settings.ALLOCATION_GLOBAL_READ_ROLES,
        settings.ALLOCATION_SYSTEM_ADMIN_ROLES
        + settings.ALLOCATION_SYSTEM_APPROVER_ROLES
        + settings.ALLOCATION_SYSTEM_READ_ROLES,
    )


def is_write_admin(user):
    return has_roles(
        user,
        settings.ALLOCATION_GLOBAL_ADMIN_ROLES
        + settings.ALLOCATION_APPROVER_ROLES,
        settings.ALLOCATION_SYSTEM_ADMIN_ROLES
        + settings.ALLOCATION_SYSTEM_APPROVER_ROLES,
    )


class PermissionMixin:
    def is_read_admin(self):
        return is_read_admin(self.request.user)

    def is_write_admin(self):
        return is_write_admin(self.request.user)
