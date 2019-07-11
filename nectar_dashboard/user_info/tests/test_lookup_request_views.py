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


class LookupLookupMixin():
    url = reverse('horizon:identity:lookup:lookup')


class AdminLookupLookupTestCase(LookupLookupMixin, base.AdminViewTestCase):
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

    def test_post_known_user(self):
        form = {'email': self.rcs_user.email}
        response = self.client.post(self.url, form)
        self.assertStatusCode(response, 302)
        self.assertEqual(response.get('location'),
                         reverse('horizon:identity:lookup:list',
                                 args=[self.rcs_user.email]))


class UserLookupLookupTestCase(LookupLookupMixin, base.UserViewTestCase):
    def test_get(self):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 403)

    def test_post(self):
        response = self.client.post(self.url)
        self.assertStatusCode(response, 403)


class LookupListMixin():
    def get_url(self):
        return reverse('horizon:identity:lookup:list',
                       args=[self.rcs_user.email])


class UserLookupListTestCase(LookupListMixin, base.UserViewTestCase):
    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertStatusCode(response, 403)

    def test_post(self):
        response = self.client.post(self.get_url())
        self.assertStatusCode(response, 403)


class AdminLookupListTestCase(LookupListMixin, base.AdminViewTestCase):
    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertStatusCode(response, 200)
        self.assertEqual(len(response.context_data['table'].get_rows()), 1)

    def test_get_unknown(self):
        unknown_url = reverse('horizon:identity:lookup:list', args=[9999])
        response = self.client.get(unknown_url)
        self.assertStatusCode(response, 200)
        self.assertEqual(len(response.context_data['table'].get_rows()), 0)

    def test_post(self):
        response = self.client.post(self.get_url())
        self.assertStatusCode(response, 200)


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
