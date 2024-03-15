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
class BundleTest(base.AllocationAPITest):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.bundle = models.Bundle.objects.get(name='gold')

    def test_list_bundles(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/bundles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        total = models.Bundle.objects.count()
        self.assertEqual(total, len(response.data['results']))

    def test_list_bundles_unauthenticated(self):
        response = self.client.get('/rest_api/bundles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        total = models.Bundle.objects.count()
        self.assertEqual(total, len(response.data['results']))

    def test_get_bundle(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/rest_api/bundles/{self.bundle.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.bundle.id, response.data['id'])
        self.assertEqual(self.bundle.name, response.data['name'])
        self.assertEqual(self.bundle.description, response.data['description'])
        self.assertEqual(self.bundle.zone.name, response.data['zone'])
        self.assertEqual(self.bundle.quota_list(), response.data['quotas'])

    def test_create_bundle(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'platinum',
                'description': 'lots and lots',
                'zone': 'nectar',
                'su_per_year': 20000,
                'order': 10}
        response = self.client.post('/rest_api/bundles/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        b = models.Bundle.objects.get(name='platinum')
        self.assertEqual(data['name'], b.name)
        self.assertEqual(data['description'], b.description)
        self.assertEqual(data['zone'], b.zone.name)
        self.assertEqual(data['order'], b.order)

    def test_update_bundle(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'description': 'Very good'}
        response = self.client.patch(f'/rest_api/bundles/{self.bundle.id}/',
                                     data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        b = models.Bundle.objects.get(id=self.bundle.id)
        self.assertEqual(data['description'], b.description)

    def test_delete_bundle(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/rest_api/bundles/{self.bundle.id}/')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
