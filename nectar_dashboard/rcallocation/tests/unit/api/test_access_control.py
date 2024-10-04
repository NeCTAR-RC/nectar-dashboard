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


@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class AccessControlTest(base.AllocationAPITest):
    endpoints = [
        'ncris-facilities',
        'zones',
        'service-types',
        'sites',
        'ardc-projects',
        'resources',
    ]

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        for e in self.endpoints:
            response = self.client.get(f'/rest_api/{e}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_unauthenticated(self):
        for e in self.endpoints:
            response = self.client.get(f'/rest_api/{e}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_no_permission(self):
        self.client.force_authenticate(user=self.user)
        for e in self.endpoints:
            response = self.client.post(f'/rest_api/{e}/', {})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_no_permission(self):
        self.client.force_authenticate(user=self.user)
        for e in self.endpoints:
            response = self.client.patch(f'/rest_api/{e}/xxx/', {})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete(self):
        self.client.force_authenticate(user=self.admin_user)
        for e in self.endpoints:
            response = self.client.delete(f'/rest_api/{e}/XXX/')
            self.assertEqual(
                response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )

    def test_delete_no_permission(self):
        self.client.force_authenticate(user=self.user)
        for e in self.endpoints:
            response = self.client.delete(f'/rest_api/{e}/XXX/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
