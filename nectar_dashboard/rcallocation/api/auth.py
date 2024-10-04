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


class PermissionMixin:
    def is_read_admin(self):
        if self.request.user.is_authenticated:
            roles = set(
                [role['name'].lower() for role in self.request.user.roles]
            )
            required = set(
                settings.ALLOCATION_GLOBAL_ADMIN_ROLES
                + settings.ALLOCATION_APPROVER_ROLES
                + settings.ALLOCATION_GLOBAL_READ_ROLES
            )
            if required & roles:
                return True
        return False

    def is_write_admin(self):
        if self.request.user.is_authenticated:
            roles = set(
                [role['name'].lower() for role in self.request.user.roles]
            )
            required = set(
                settings.ALLOCATION_GLOBAL_ADMIN_ROLES
                + settings.ALLOCATION_APPROVER_ROLES
            )
            if required & roles:
                return True
        return False


def is_write_admin(user):
    if user.is_authenticated:
        roles = set([role['name'].lower() for role in user.roles])
        required = set(
            settings.ALLOCATION_GLOBAL_ADMIN_ROLES
            + settings.ALLOCATION_APPROVER_ROLES
        )
        if required & roles:
            return True
    return False
