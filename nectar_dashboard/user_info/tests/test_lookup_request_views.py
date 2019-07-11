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

# from nectar_dashboard.user_info import models

from . import base
# from . import common


class LookupViewTestCase(base.AdminViewTestCase):
    url = reverse('horizon:identity:lookup:lookup')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 200)


class UserLookupViewTestCase(base.UserViewTestCase):
    url = reverse('horizon:identity:lookup:lookup')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 302)
        self.assertEqual(response.get('location'),
                         "/auth/login/?next=" + self.url)
