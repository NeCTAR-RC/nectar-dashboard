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

from rest_framework import status

from nectar_dashboard.rcallocation.tests import base


class FORTests(base.AllocationAPITest):

    def test_for_codes(self):
        response = self.client.get('/rest_api/for-codes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for_dict = response.data
        self.assertIn('0599', for_dict)
        self.assertEqual('OTHER ENVIRONMENTAL SCIENCES', for_dict['0599'])

    def test_for_tree(self):
        self.maxDiff = 10000
        response = self.client.get('/rest_api/for-tree/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tree = response.data
        self.assertIn('name', tree.keys())
        self.assertIn('children', tree.keys())
        self.assertEqual('allocations', tree['name'])
        for child in tree['children']:
            name = child['name']
            grandchildren = child['children']
            for grandchild in grandchildren:
                self.assertTrue(grandchild['name'].startswith(name))
