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
class FacilitiesTest(base.AllocationAPITest):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # The 0058 migration populates the initial facilities
        self.ala = models.NCRISFacility.objects.get(short_name='ALA')

    def test_list_facilities(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/ncris-facilities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(22, len(response.data['results']))

    def test_list_facilities_unauthenticated(self):
        response = self.client.get('/rest_api/ncris-facilities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(22, len(response.data['results']))

    def test_create_facility_no_permission(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Applied Magic Facility'}
        response = self.client.post('/rest_api/ncris-facilities/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_facility_duplicate(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Astronomy Australia Ltd'}
        response = self.client.post('/rest_api/ncris-facilities/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_facility(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Applied Magic Facility', 'short_name': 'AMF'}
        response = self.client.post('/rest_api/ncris-facilities/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_facility(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Atlas of Lovely Australia'}
        response = self.client.patch(
            f'/rest_api/ncris-facilities/{self.ala.id}/', data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_facility(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            f'/rest_api/ncris-facilities/{self.ala.id}/'
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
