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


class UpdateViewsTestCase(base.BaseTestCase):

    def test_get(self):
        url = reverse('horizon:settings:update:edit-self')
        response = self.client.get(url)
        self.assertStatusCode(response, 200)
        self.assertEqualUsers(self.rcs_user, response.context_data['object'])

    def test_post_no_change(self):
        url = reverse('horizon:settings:update:edit-self')
        response = self.client.get(url)
        self.assertStatusCode(response, 200)
        form = common.user_to_dict(self.rcs_user)
        response = self.client.post(url, form)
        self.assertStatusCode(response, 302)
        # self.assertEqualUsers(self.rcs_user, response.context_data['object'])
        user = models.User.objects.get(user_id=self.rcs_user.user_id)
        self.assertEqualUsers(self.rcs_user, user)

    def test_post_name_change(self):
        url = reverse('horizon:settings:update:edit-self')
        self.maxDiff = 9999
        response = self.client.get(url)
        self.assertStatusCode(response, 200)
        form = common.user_to_dict(self.rcs_user)
        form['displayname'] = "Jim Spriggs"
        form['first_name'] = "Jim"
        form['surname'] = "Spriggs"
        response = self.client.post(url, form)
        self.assertStatusCode(response, 302)
        # Change should be ignored
        user = models.User.objects.get(user_id=self.rcs_user.user_id)
        self.assertEqualUsers(user, self.rcs_user)

    def test_post_orcid_change(self):
        url = reverse('horizon:settings:update:edit-self')
        response = self.client.get(url)
        self.assertStatusCode(response, 200)
        form = common.user_to_dict(self.rcs_user)
        form['orcid'] = "rose"
        response = self.client.post(url, form)
        self.assertStatusCode(response, 302)
        # Change should be made
        user = models.User.objects.get(user_id=self.rcs_user.user_id)
        self.assertEqualUsers(user, form)
