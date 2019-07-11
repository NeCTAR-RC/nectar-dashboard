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
from openstack_dashboard.test import helpers

from . import common


class BaseTestCase(helpers.BaseAdminViewTests):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        common.factory_setup()
        self.rcs_user = common.UserFactory(email="joe.smith@gmail.com")
        self.setActiveUser(id=self.rcs_user.user_id,
                           username=self.rcs_user.persistent_id,
                           token=self.token,
                           service_catalog=self.service_catalog,
                           tenant_id=self.tenant.id)

    def assertEqualUsers(self, user1, user2):
        self.assertEqual(user1.id, user2.id)
        self.assertEqual(user1.user_id, user2.user_id)
        self.assertEqual(user1.displayname, user2.displayname)
        self.assertEqual(user1.persistent_id, user2.persistent_id)
        self.assertEqual(user1.email, user2.email)
        self.assertEqual(user1.state, user2.state)
        self.assertEqual(user1.terms_accepted_at,
                          user2.terms_accepted_at)
        self.assertEqual(user1.shibboleth_attributes,
                          user2.shibboleth_attributes)
        self.assertEqual(user1.registered_at, user2.registered_at)
        self.assertEqual(user1.terms_version, user2.terms_version)
        self.assertEqual(user1.ignore_username_not_email,
                          user2.ignore_username_not_email)
        self.assertEqual(user1.first_name, user2.first_name)
        self.assertEqual(user1.surname, user2.surname)
        self.assertEqual(user1.phone_number, user2.phone_number)
        self.assertEqual(user1.mobile_number, user2.mobile_number)
        self.assertEqual(user1.home_organization,
                          user2.home_organization)
        self.assertEqual(user1.orcid, user2.orcid)
        self.assertEqual(user1.affiliation, user2.affiliation)


class UpdateViewsTestCase(BaseTestCase):

    def test_get(self):
        url = reverse('horizon:settings:update:edit-self')
        response = self.client.get(url)
        self.assertStatusCode(response, 200)
        self.assertEqualUsers(self.rcs_user, response.context_data['object'])
