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

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base


@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class ApproverTest(base.AllocationAPITest):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.qcif = models.Site.objects.get(name='qcif')
        self.uom = models.Site.objects.get(name='uom')
        # Delete all the existing approvers setup in base
        models.Approver.objects.all().delete()
        self.assertEqual(models.Approver.objects.all().count(), 0)
        self.jim = models.Approver.objects.create(
            username='jim.spriggs@uq.edu.au',
            display_name='Jim Spriggs')
        self.jim.sites.add(self.qcif)
        self.jim.save()

    def test_list_approvers(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/rest_api/approvers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_approvers_as_approver(self):
        self.client.force_authenticate(user=self.approver_user)
        response = self.client.get('/rest_api/approvers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_approvers_unauthenticated(self):
        response = self.client.get('/rest_api/approvers/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_approver(self):
        data = {'username': 'joe.bloggs@uq.edu.au',
                'display_name': 'Joseph Bloggs',
                'sites': [self.qcif.id]}
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/rest_api/approvers/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        joe = models.Approver.objects.get(username='joe.bloggs@uq.edu.au')
        self.assertEqual(joe.username, 'joe.bloggs@uq.edu.au')
        self.assertEqual(joe.display_name, 'Joseph Bloggs')
        sites = list(joe.sites.all())
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites[0].id, self.qcif.id)

    def test_create_approver_no_permission(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'darwin'}
        response = self.client.post('/rest_api/approvers/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_approver_duplicate(self):
        data = {'username': 'jim.spriggs@uq.edu.au',
                'display_name': 'Joseph Bloggs',
                'sites': [self.qcif.id]}
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/rest_api/approvers/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_approver(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'display_name': 'Adolphus Spriggs',
                'sites': [self.qcif.id, self.uom.id]}
        response = self.client.patch('/rest_api/approvers/%s/' % self.jim.id,
                                     data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jim = models.Approver.objects.get(username='jim.spriggs@uq.edu.au')
        self.assertEqual(jim.username, 'jim.spriggs@uq.edu.au')
        self.assertEqual(jim.display_name, 'Adolphus Spriggs')
        sites = list(jim.sites.all())
        self.assertEqual(len(sites), 2)
        self.assertTrue(self.qcif.id in (s.id for s in sites))
        self.assertTrue(self.uom.id in (s.id for s in sites))

    def test_delete_approver(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete('/rest_api/approvers/%s/' % self.jim.id)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
