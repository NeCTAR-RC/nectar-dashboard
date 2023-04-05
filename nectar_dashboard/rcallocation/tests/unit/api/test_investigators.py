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
from nectar_dashboard.rcallocation.tests import factories


@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class InvestigatorTests(base.AllocationAPITest):

    def setUp(self):
        super().setUp()
        self.ci = factories.InvestigatorFactory(
            allocation=self.allocation,
            primary_organisation=models.Organisation.objects.get(
                short_name="Monash"))

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/chiefinvestigators/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(models.ChiefInvestigator.objects.filter(
            allocation__contact_email=self.user.username)),
                         len(response.data['results']))
        self.assertEqual(1, len(response.data['results']))

    def test_list_unauthenticated(self):
        response = self.client.get('/rest_api/chiefinvestigators/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_other(self):
        # Don't list the CIs for another user's allocations
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/rest_api/chiefinvestigators/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data['results']))

    def test_list_admin(self):
        # An admin can see all allocations' CIs
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/rest_api/chiefinvestigators/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/chiefinvestigators/%s/' %
                                   self.ci.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.ci.id, response.data['id'])

    def test_get_unauthenticated(self):
        response = self.client.get('/rest_api/chiefinvestigators/%s/' %
                                   self.ci.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_other(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/rest_api/chiefinvestigators/%s/' %
                                   self.ci.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/rest_api/chiefinvestigators/%s/' %
                                   self.ci.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.ci.id, response.data['id'])

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/rest_api/chiefinvestigators/%s/' %
                                     self.ci.id,
                                     {'given_name': 'Cholmondely'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Cholmondely', response.data['given_name'])

    def test_update_wrong_state(self):
        self.client.force_authenticate(user=self.user)
        self.allocation.status = models.AllocationRequest.APPROVED
        self.allocation.save()
        response = self.client.patch('/rest_api/chiefinvestigators/%s/' %
                                     self.ci.id,
                                     {'given_name': 'Maxwell'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/rest_api/chiefinvestigators/%s/' %
                                      self.ci.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_state(self):
        self.client.force_authenticate(user=self.user)
        self.allocation.status = models.AllocationRequest.APPROVED
        self.allocation.save()
        response = self.client.delete('/rest_api/chiefinvestigators/%s/' %
                                      self.ci.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_user(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete('/rest_api/chiefinvestigators/%s/' %
                                      self.ci.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _make_data(self):
        return {
            'allocation': self.allocation.id,
            'given_name': 'Joe',
            'surname': 'Bloggs',
            'title': 'Mr',
            'email': 'joe@monash.edu',
            'primary_organisation': models.Organisation.objects.get(
                short_name='Monash'),
        }

    def test_create(self):
        # This doesn't strictly make sense because we are actually
        # adding a 2nd CI record.
        for user in [self.user, self.approver_user]:
            self.client.force_authenticate(user=user)
            data = self._make_data()
            response = self.client.post('/rest_api/chiefinvestigators/', data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            ci = models.ChiefInvestigator.objects.get(id=response.data['id'])
            self.assertEqual('Bloggs', ci.surname)
            self.assertEqual(self.allocation, ci.allocation)

    def test_create_wrong_state(self):
        self.client.force_authenticate(user=self.user)
        self.allocation.status = models.AllocationRequest.APPROVED
        self.allocation.save()
        data = self._make_data()
        response = self.client.post('/rest_api/chiefinvestigators/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_unauthenticated(self):
        data = self._make_data()
        response = self.client.post('/rest_api/chiefinvestigators/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
