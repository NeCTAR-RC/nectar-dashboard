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
from nectar_dashboard.rcallocation.tests import factories

from nectar_dashboard.rcallocation import models


@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class SiteTest(base.AllocationAPITest):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.uom = models.Site.objects.get(name='uom')

    def test_list_sites(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/sites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(factories.ALL_SITES),
                         len(response.data['results']))

    def test_list_sites_unauthenticated(self):
        response = self.client.get('/rest_api/sites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(factories.ALL_SITES),
                         len(response.data['results']))

    def test_create_site_no_permission(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'darwin'}
        response = self.client.post('/rest_api/sites/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_site_duplicate(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'uom'}
        response = self.client.post('/rest_api/sites/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_site(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'darwin',
                'display_name': 'Darwin University'}
        response = self.client.post('/rest_api/sites/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_site(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'display_name': 'University of Darwin'}
        response = self.client.patch('/rest_api/sites/%s/' % self.uom.id, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_site(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete('/rest_api/sites/%s/' % self.uom.id)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
