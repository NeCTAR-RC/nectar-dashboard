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

import mock

from rest_framework import status

from nectar_dashboard.rcallocation import models

from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories


@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class AllocationTests(base.AllocationAPITest):

    def test_list_allocations(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))

    def test_list_allocations_unauthenticated(self):
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_allocations_negative(self):
        self.client.force_authenticate(user=self.user)
        factories.AllocationFactory.create(contact_email='other@example.com')
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))

    def test_list_allocations_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.AllocationFactory.create(contact_email='other@example.com')
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))

    def test_get_allocation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/allocations/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, response.data['id'])
        for field in ['notes', 'status_explanation']:
            self.assertNotIn(field, response.data.keys())

    def test_get_allocation_unauthenticated(self):
        response = self.client.get('/rest_api/allocations/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        public_fields = ['id', 'project_name', 'project_description',
                         'modified_time', 'submit_date', 'start_date',
                         'end_date', 'field_of_research_1',
                         'field_of_research_2', 'field_of_research_3',
                         'for_percentage_1', 'for_percentage_2',
                         'for_percentage_3', 'quotas']
        self.assertEqual(public_fields, response.data.keys())

    def test_get_allocation_negative(self):
        self.client.force_authenticate(user=self.user)
        factories.AllocationFactory.create(contact_email='other@example.com')
        response = self.client.get('/rest_api/allocations/2/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_allocation_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.AllocationFactory.create(contact_email='other@example.com')
        response = self.client.get('/rest_api/allocations/2/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, response.data['id'])
        self.assertIn('notes', response.data.keys())

    def test_update_allocation(self):
        self.client.force_authenticate(user=self.user)
        self.assertNotEqual('test-update', self.allocation.use_case)
        response = self.client.patch('/rest_api/allocations/1/',
                                     {'use_case': 'test-update'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id)
        self.assertEqual('test-update', allocation.use_case)

    def test_update_allocation_invalid_state(self):
        self.client.force_authenticate(user=self.user)
        allocation = factories.AllocationFactory.create(
            status=models.AllocationRequest.APPROVED,
            contact_email=self.user.username)
        response = self.client.patch(
            '/rest_api/allocations/%s/' % allocation.id,
            {'use_case': 'test-update'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_allocation_read_only_field(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            '/rest_api/allocations/1/',
            {'status': models.AllocationRequest.APPROVED})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # It returns 200 but value doesn't change
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id)
        self.assertEqual(self.allocation.status, allocation.status)

    def test_update_allocation_unauthenticated(self):
        response = self.client.patch('/rest_api/allocations/1/',
                                     {'use_case': 'test-update'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_allocation_negative(self):
        self.client.force_authenticate(user=self.user)
        factories.AllocationFactory.create(contact_email='other@example.com')
        response = self.client.patch('/rest_api/allocations/2/',
                                     {'use_case': 'test-update'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_allocation_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.AllocationFactory.create(contact_email='other@example.com')
        response = self.client.patch('/rest_api/allocations/2/',
                                     {'use_case': 'test-update'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('test-update', response.data['use_case'])

    def test_update_allocation_admin_field(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.AllocationFactory.create(contact_email='other@example.com')
        response = self.client.patch('/rest_api/allocations/2/',
                                     {'notes': 'test-notes'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('test-notes', response.data['notes'])

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'allocation_home': 'uom',
                'use_case': 'for testing'}
        response = self.client.post('/rest_api/allocations/', data)
        allocation = models.AllocationRequest.objects.get(id=2)
        self.assertEqual(self.user.token.project['id'], allocation.created_by)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('test-project', response.data['project_name'])
        self.assertEqual(self.user.username, response.data['contact_email'])
        self.assertEqual(models.AllocationRequest.SUBMITTED,
                         response.data['status'])

    def test_create_override_contact_email(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'allocation_home': 'uom',
                'use_case': 'for testing',
                'contact_email': 'test_override@example.com'}
        response = self.client.post('/rest_api/allocations/', data)
        allocation = models.AllocationRequest.objects.get(id=2)
        self.assertEqual(self.admin_user.token.project['id'],
                         allocation.created_by)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('test-project', response.data['project_name'])
        self.assertEqual('test_override@example.com',
                         response.data['contact_email'])
        self.assertEqual(models.AllocationRequest.SUBMITTED,
                         response.data['status'])

    def test_create_duplicate_project_name(self):
        self.client.force_authenticate(user=self.user)
        factories.AllocationFactory.create(project_name='test-project')
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'allocation_home': 'uom',
                'use_case': 'for testing'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_unathenticated(self):
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'allocation_home': 'uom',
                'use_case': 'for testing'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve(self):
        self.client.force_authenticate(user=self.approver_user)
        response = self.client.post(
            '/rest_api/allocations/%s/approve/' % self.allocation.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.AllocationRequest.APPROVED,
                         response.data['status'])

    def test_approve_invalid_state(self):
        self.client.force_authenticate(user=self.approver_user)
        allocation = factories.AllocationFactory.create(
            status=models.AllocationRequest.APPROVED)
        response = self.client.post(
            '/rest_api/allocations/%s/approve/' % allocation.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_invalid_role(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/rest_api/allocations/%s/approve/' % self.allocation.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_amend(self):
        self.client.force_authenticate(user=self.user)
        allocation = factories.AllocationFactory.create(
            contact_email=self.user.username,
            status=models.AllocationRequest.APPROVED)
        response = self.client.post(
            '/rest_api/allocations/%s/amend/' % allocation.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(id=allocation.id)
        self.assertEqual(models.AllocationRequest.UPDATE_PENDING,
                         allocation.status)

    def test_amend_invalid_state(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest_api/allocations/1/amend/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_amend_invalid_user(self):
        self.client.force_authenticate(user=self.user)
        allocation = factories.AllocationFactory.create(
            contact_email='bogus@wrong.com',
            status=models.AllocationRequest.APPROVED)
        response = self.client.post(
            '/rest_api/allocations/%s/amend/' % allocation.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/rest_api/allocations/1/delete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.AllocationRequest.DELETED,
                         response.data['status'])

    def test_delete_invalid_role(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest_api/allocations/1/delete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/rest_api/allocations/1/')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
