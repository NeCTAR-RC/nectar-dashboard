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

from . import common


class BaseTestCase(helpers.BaseAdminViewTests):

    def setUp(self):
        super().setUp()
        common.factory_setup()
        self.rcs_user = common.RCUserFactory(email="joe.smith@gmail.com")

    def assertEqualUsers(self, user1, user2, ignore=[]):
        """Assert two RCS users are the same.  The users can be represented
        as User model objects or as dicts.  The 'ignore' argument is a
        list of keys / attributes to ignore when comparing.
        """
        dict1 = user1 if type(user1) is dict else common.user_to_dict(user1)
        dict2 = user2 if type(user2) is dict else common.user_to_dict(user2)
        for k in ignore:
            dict1.pop(k, None)
            dict2.pop(k, None)
        self.assertEqual(dict1, dict2)


class UserViewTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.setActiveUser(id=self.rcs_user.user_id,
                           username=self.rcs_user.persistent_id,
                           token=self.token,
                           service_catalog=self.service_catalog,
                           tenant_id=self.tenant.id)


class AdminViewTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        allocation_admin_role_dict = {'id': '142',
                                      'name': 'allocationadmin'}
        allocation_admin_role = roles.Role(roles.RoleManager,
                                           allocation_admin_role_dict,
                                           loaded=True)
        self.roles.add(allocation_admin_role)
        self.roles.allocation_admin = allocation_admin_role
        self.setActiveUser(id=self.rcs_user.user_id,
                           username=self.rcs_user.persistent_id,
                           token=self.token,
                           service_catalog=self.service_catalog,
                           tenant_id=self.tenant.id,
                           roles=[self.roles.allocation_admin._info])
