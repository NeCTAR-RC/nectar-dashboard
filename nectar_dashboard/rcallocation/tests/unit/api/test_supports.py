#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from unittest import mock

from rest_framework import status

from nectar_dashboard.rcallocation.tests import base

from nectar_dashboard.rcallocation import models


@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class SupportsTest(base.AllocationAPITest):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # The 0060 migration populates the initial ARDC programs and projects
        self.cvl = models.ARDCSupport.objects.get(short_name='CVL')

    def test_list_projects(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/ardc-projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(78, len(response.data['results']))

    def test_list_projects_unauthenticated(self):
        response = self.client.get('/rest_api/ardc-projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(78, len(response.data['results']))

    def test_create_project_no_permission(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Applied Magic Project'}
        response = self.client.post('/rest_api/ardc-projects/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_project_duplicate(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Astronomy Australia Ltd'}
        response = self.client.post('/rest_api/ardc-projects/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_project(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'Applied Magic Project',
            'short_name': 'AMF',
            'rank': 50,
        }
        response = self.client.post('/rest_api/ardc-projects/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_project(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Chimeric Virtual Laboratory'}
        response = self.client.patch(
            f'/rest_api/ardc-projects/{self.cvl.id}/', data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_project(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            f'/rest_api/ardc-projects/{self.cvl.id}/'
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
