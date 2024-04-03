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

from unittest import mock

from django.urls import reverse
from nectarclient_lib import exceptions

from . import base


USER_ID = '123'


class ListMixin(object):
    url = reverse('horizon:identity:lookup:list')


@mock.patch('nectar_dashboard.api.manuka.manukaclient')
class AdminListUserTestCase(ListMixin, base.AdminViewTestCase):

    def test_get(self, mock_get_manuka):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 200)

    def test_get_no_params(self, mock_get_manuka):
        response = self.client.get(self.url, {})
        self.assertStatusCode(response, 200)
        self.assertEqual(0, len(response.context_data['table'].get_rows()))

    def test_get_search(self, mock_get_manuka):
        client = mock_get_manuka.return_value
        client.users.search.return_value = [mock.Mock(id=USER_ID)]
        response = self.client.get(self.url, {'q': 'needle'})
        client.users.search.assert_called_once_with('needle')
        self.assertStatusCode(response, 200)
        self.assertEqual(1, len(response.context_data['table'].get_rows()))

    def test_get_search_unknown(self, mock_get_manuka):
        response = self.client.get(self.url, {'q': "xxx@example.com"})
        client = mock_get_manuka.return_value
        client.users.search.return_value = []
        self.assertStatusCode(response, 200)
        self.assertEqual(0, len(response.context_data['table'].get_rows()))

    def test_post(self, mock_get_manuka):
        response = self.client.post(self.url)
        self.assertStatusCode(response, 200)


class ListUserTestCase(ListMixin, base.UserViewTestCase):

    def test_get(self):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 403)

    def test_post(self):
        response = self.client.post(self.url)
        self.assertStatusCode(response, 403)


class ViewMixin(object):
    def get_url(self):
        return reverse('horizon:identity:lookup:view',
                       args=[USER_ID])


class ViewUserTestCase(ViewMixin, base.UserViewTestCase):

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertStatusCode(response, 403)

    def test_post(self):
        response = self.client.post(self.get_url())
        self.assertStatusCode(response, 403)


@mock.patch('nectar_dashboard.api.manuka.manukaclient')
class AdminViewUserTestCase(ViewMixin, base.AdminViewTestCase):

    def test_get(self, mock_get_manuka):
        client = mock_get_manuka.return_value
        mock_user = mock.Mock()
        mock_user.external_ids = [mock.Mock(idp='idp', last_login='sometime')]
        client.users.get.return_value = mock_user
        response = self.client.get(self.get_url())
        self.assertStatusCode(response, 200)
        self.assertEqual(mock_user.id, response.context_data['object'].id)
        client.users.get.assert_called_once_with(USER_ID)

    def test_get_unknown(self, mock_get_manuka):
        client = mock_get_manuka.return_value
        client.users.get.side_effect = exceptions.NotFound
        unknown_url = reverse('horizon:identity:lookup:view', args=[9999])
        response = self.client.get(unknown_url)
        self.assertStatusCode(response, 302)

    def test_post(self, mock_get_manuka):
        response = self.client.post(self.get_url())
        self.assertStatusCode(response, 405)
