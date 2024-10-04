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

from nectar_dashboard.user_info.tests import base


@mock.patch('nectar_dashboard.api.manuka.manukaclient')
class EditSelfViewTestCase(base.UserViewTestCase):
    url = reverse('horizon:settings:my-details:edit-self')

    def test_get(self, mock_get_manuka):
        client = mock_get_manuka.return_value
        manuka_user = client.users.get.return_value
        response = self.client.get(self.url)
        self.assertStatusCode(response, 200)
        self.assertEqual(manuka_user, response.context_data['object'])
        client.users.get.assert_called_once_with(
            self.request.user.keystone_user_id
        )

    def test_post_bad_form(self, mock_get_manuka):
        client = mock_get_manuka.return_value
        manuka_user = client.users.get.return_value

        form = {
            'affiliation': 'member',
            'phone_number': '123',
            'mobile_number': '456',
            'orcid': 'rose',
        }

        # Can't change displayname
        form['displayname'] = "Jim Spriggs"
        response = self.client.post(self.url, form)
        # Invalid values should be ignored
        form.pop('displayname')
        self.assertStatusCode(response, 302)
        self.assertEqual(response.get('location'), self.url)
        client.users.update.assert_called_once_with(
            manuka_user.to_dict()['id'], **form
        )

    def test_post_change(self, mock_get_manuka):
        client = mock_get_manuka.return_value
        manuka_user = client.users.get.return_value

        form = {
            'affiliation': 'member',
            'phone_number': '123',
            'mobile_number': '456',
            'orcid': 'rose',
        }
        response = self.client.post(self.url, form)
        self.assertStatusCode(response, 302)
        self.assertEqual(response.get('location'), self.url)
        client.users.update.assert_called_once_with(
            manuka_user.to_dict()['id'], **form
        )
