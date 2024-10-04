# Copyright 2019 Australian Research Data Commons
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from openstack_dashboard.test import helpers

from keystoneclient.v3 import roles


class UserViewTestCase(helpers.TestCase):
    pass


class AdminViewTestCase(helpers.BaseAdminViewTests):
    def setActiveUser(self, *args, **kwargs):
        if "roles" not in kwargs:
            allocation_admin_role_dict = {
                'id': '142',
                'name': 'allocationadmin',
            }
            allocation_admin_role = roles.Role(
                roles.RoleManager, allocation_admin_role_dict, loaded=True
            )
            self.roles.add(allocation_admin_role)
            self.roles.allocation_admin = allocation_admin_role
            kwargs['roles'] = [self.roles.allocation_admin._info]
            super().setActiveUser(*args, **kwargs)
