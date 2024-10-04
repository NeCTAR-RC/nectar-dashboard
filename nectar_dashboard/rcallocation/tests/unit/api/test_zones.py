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

from django.conf import settings
from rest_framework import status

from nectar_dashboard.rcallocation.tests import base


@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class ZoneTests(base.AllocationAPITest):
    def test_compute_homes(self):
        response = self.client.get('/rest_api/zones/compute_homes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(settings.ALLOCATION_HOME_ZONE_MAPPINGS, response.data)
