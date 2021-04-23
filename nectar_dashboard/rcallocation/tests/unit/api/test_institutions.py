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
class InstitutionTests(base.AllocationAPITest):

    def test_list_institutions(self):
        self.client.force_authenticate(user=self.user)
        factories.InstitutionFactory(allocation=self.allocation)
        factories.InstitutionFactory(allocation=self.allocation, name='foo')
        response = self.client.get('/rest_api/institutions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(models.Institution.objects.filter(
            allocation__contact_email=self.user.username)),
                         len(response.data['results']))

    def test_list_institutions_unauthenticated(self):
        response = self.client.get('/rest_api/institutions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_institutions_negative(self):
        self.client.force_authenticate(user=self.user2)
        factories.InstitutionFactory(allocation=self.allocation)
        factories.InstitutionFactory(allocation=self.allocation, name='foo')
        response = self.client.get('/rest_api/institutions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(models.Institution.objects.filter(
            allocation__contact_email=self.user2.username)),
                         len(response.data['results']))

    def test_list_institutions_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.InstitutionFactory(allocation=self.allocation)
        factories.InstitutionFactory(allocation=self.allocation, name='foo')
        response = self.client.get('/rest_api/institutions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Institution.objects.count(),
                         len(response.data['results']))

    def test_get_institution(self):
        self.client.force_authenticate(user=self.user)
        institution = factories.InstitutionFactory(allocation=self.allocation)
        response = self.client.get('/rest_api/institutions/%s/' %
                                   institution.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(institution.id, response.data['id'])

    def test_get_institution_unauthenticated(self):
        institution = factories.InstitutionFactory(allocation=self.allocation)
        response = self.client.get('/rest_api/institutions/%s/' %
                                   institution.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_institution_negative(self):
        self.client.force_authenticate(user=self.user2)
        institution = factories.InstitutionFactory(allocation=self.allocation)
        response = self.client.get('/rest_api/institutions/%s/' %
                                   institution.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_institution_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        institution = factories.InstitutionFactory(allocation=self.allocation)
        response = self.client.get('/rest_api/institutions/%s/' %
                                   institution.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_institution(self):
        self.client.force_authenticate(user=self.user)
        institution = factories.InstitutionFactory(allocation=self.allocation)
        response = self.client.patch('/rest_api/institutions/%s/' %
                                     institution.id,
                                     {'name': 'new-name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('new-name', response.data['name'])

    def test_update_institution_wrong_state(self):
        self.client.force_authenticate(user=self.user)
        self.allocation.status = models.AllocationRequest.APPROVED
        self.allocation.save()
        institution = factories.InstitutionFactory(allocation=self.allocation)
        response = self.client.patch('/rest_api/institutions/%s/' %
                                     institution.id,
                                     {'name': 'new-name'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_institution(self):
        self.client.force_authenticate(user=self.user)
        institution = factories.InstitutionFactory(allocation=self.allocation)
        response = self.client.delete('/rest_api/institutions/%s/' %
                                      institution.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_institution_invalid_state(self):
        self.client.force_authenticate(user=self.user)
        self.allocation.status = models.AllocationRequest.APPROVED
        self.allocation.save()
        institution = factories.InstitutionFactory(allocation=self.allocation)
        response = self.client.delete('/rest_api/institutions/%s/' %
                                      institution.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_institution_negative(self):
        self.client.force_authenticate(user=self.user2)
        institution = factories.InstitutionFactory(allocation=self.allocation)
        response = self.client.delete('/rest_api/institutions/%s/' %
                                      institution.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'allocation': self.allocation.id,
            'name': 'foobar',
        }
        response = self.client.post('/rest_api/institutions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        institution = models.Institution.objects.get(id=response.data['id'])
        self.assertEqual('foobar', institution.name)
        self.assertEqual(self.allocation, institution.allocation)

    def test_create_approver(self):
        self.client.force_authenticate(user=self.approver_user)
        data = {
            'allocation': self.allocation.id,
            'name': 'foobar',
        }
        response = self.client.post('/rest_api/institutions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        institution = models.Institution.objects.get(id=response.data['id'])
        self.assertEqual('foobar', institution.name)
        self.assertEqual(self.allocation, institution.allocation)

    def test_create_wrong_state(self):
        self.client.force_authenticate(user=self.user)
        self.allocation.status = models.AllocationRequest.APPROVED
        self.allocation.save()
        data = {
            'allocation': self.allocation.id,
            'name': 'foobar',
        }
        response = self.client.post('/rest_api/institutions/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'allocation': self.allocation.id,
            'name': 'foobar',
        }
        response = self.client.post('/rest_api/institutions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Add it again and fail
        response = self.client.post('/rest_api/institutions/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_unauthenticated(self):
        data = {
            'allocation': self.allocation.id,
            'name': 'foobar',
        }
        response = self.client.post('/rest_api/institutions/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
