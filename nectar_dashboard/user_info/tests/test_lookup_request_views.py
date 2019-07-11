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

from . import base


class LookupListMixin():
    url = reverse('horizon:identity:lookup:list')


class AdminLookupLookupTestCase(LookupListMixin, base.AdminViewTestCase):
    def test_get(self):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 200)

    def test_get_no_params(self):
        response = self.client.get(self.url, {})
        self.assertStatusCode(response, 200)
        self.assertEqual(len(response.context_data['table'].get_rows()), 0)

    def test_get_search_email(self):
        response = self.client.get(self.url, {'q': self.rcs_user.email})
        self.assertStatusCode(response, 200)
        self.assertEqual(len(response.context_data['table'].get_rows()), 2)

    def test_get_search_nickname(self):
        response = self.client.get(self.url, {'q': 'doc'})
        self.assertStatusCode(response, 200)
        self.assertEqual(len(response.context_data['table'].get_rows()), 2)

    def test_get_search_unknown(self):
        response = self.client.get(self.url, {'q': "xxx@example.com"})
        self.assertStatusCode(response, 200)
        self.assertEqual(len(response.context_data['table'].get_rows()), 0)

    def test_post(self):
        response = self.client.post(self.url)
        self.assertStatusCode(response, 200)


class UserLookupListTestCase(LookupListMixin, base.UserViewTestCase):
    def test_get(self):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 403)

    def test_post(self):
        response = self.client.post(self.url)
        self.assertStatusCode(response, 403)


class LookupViewMixin():
    def get_url(self):
        return reverse('horizon:identity:lookup:view',
                       args=[self.rcs_user.id])


class UserLookupViewTestCase(LookupViewMixin, base.UserViewTestCase):
    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertStatusCode(response, 403)

    def test_post(self):
        response = self.client.post(self.get_url())
        self.assertStatusCode(response, 403)


class AdminLookupViewTestCase(LookupViewMixin, base.AdminViewTestCase):
    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertStatusCode(response, 200)
        self.assertEqual(response.context_data['object'].id,
                         self.rcs_user.id)

    def test_get_unknown(self):
        unknown_url = reverse('horizon:identity:lookup:view', args=[9999])
        response = self.client.get(unknown_url)
        self.assertStatusCode(response, 404)

    def test_post(self):
        response = self.client.post(self.get_url())
        self.assertStatusCode(response, 405)
