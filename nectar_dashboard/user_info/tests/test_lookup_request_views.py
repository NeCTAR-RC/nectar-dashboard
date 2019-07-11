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

from django.urls import reverse

from keystoneclient.v3 import roles

from nectar_dashboard.user_info import models

from . import base
from . import common


class UserLookupViewTestCase(base.BaseTestCase):
    url = reverse('horizon:identity:lookup:lookup')

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

    def test_get(self):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 200)



