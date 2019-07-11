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

from nectar_dashboard.rcallocation.tests import utils

from . import common


class ViewTestCase(helpers.BaseAdminViewTests):

    def setUp(self):
        super(ViewTestCase, self).setUp()
        common.factory_setup()
        self.user = utils.get_user(id='1',
                                   username='joe.smith@gmail.com')
        self.rcs_user = common.UserFactory(email="joe.smith@gmail.com",
                                           user_id=self.user.id)

    def test_get(self):
        url = reverse('horizon:settings:update:edit-self')
        response = self.client.get(url)
        self.assertStatusCode(response, 200)
