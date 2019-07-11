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

from nectar_dashboard.user_info import models

from . import base
from . import common


class EditSelfViewTestCase(base.UserViewTestCase):
    url = reverse('horizon:settings:my-details:edit-self')

    def _fetch_user(self, user):
        return models.RCUser.objects.get(persistent_id=user.persistent_id)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertStatusCode(response, 200)
        self.assertEqualUsers(self.rcs_user, response.context_data['object'])

    def test_post_no_change(self):
        form = common.user_to_dict(self.rcs_user)
        response = self.client.post(self.url, form)
        self.assertStatusCode(response, 302)
        self.assertEqual(response.get('location'), self.url)
        self.assertEqualUsers(self.rcs_user, self._fetch_user(self.rcs_user))

    def test_post_name_change(self):
        form = common.user_to_dict(self.rcs_user)
        form['displayname'] = "Jim Spriggs"
        form['first_name'] = "Jim"
        form['surname'] = "Spriggs"
        response = self.client.post(self.url, form)
        self.assertStatusCode(response, 302)
        self.assertEqual(response.get('location'), self.url)

        # Change should be ignored
        self.assertEqualUsers(self.rcs_user, self._fetch_user(self.rcs_user))

    def test_post_orcid_change(self):
        form = common.user_to_dict(self.rcs_user)
        form['orcid'] = "rose"
        response = self.client.post(self.url, form)
        self.assertStatusCode(response, 302)
        self.assertEqual(response.get('location'), self.url)

        # Change should be made (in one record only)
        self.assertEqualUsers(form, self._fetch_user(self.rcs_user))
        self.assertEqualUsers(self.rcs_user_other,
                              self._fetch_user(self.rcs_user_other))
