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

import pdb

from django.urls import reverse

from . import base


class LookupViewTestCase(base.AdminViewTestCase):
    url = reverse('horizon:identity:lookup:lookup')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 200)

    def test_post_no_data(self):
        response = self.client.post(self.url)
        self.assertStatusCode(response, 200)
        form = response.context_data['form']
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'email': ['This field is required.']})

    def test_post_bad_email(self):
        form = {'email': "nobody"}
        response = self.client.post(self.url, form)
        self.assertStatusCode(response, 200)
        form = response.context_data['form']
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'email': ['Enter a valid email address.']})

    def test_post_unknown_user(self):
        form = {'email': "nobody@example.com"}
        response = self.client.post(self.url, form)
        self.assertStatusCode(response, 200)
        form = response.context_data['form']
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'email': ['No users match this account / email.']})
        if False:
            pdb.set_trace()


class UserLookupViewTestCase(base.UserViewTestCase):
    url = reverse('horizon:identity:lookup:lookup')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 403)

    def test_POST(self):
        response = self.client.post(self.url)
        self.assertStatusCode(response, 403)
