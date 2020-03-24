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

import datetime
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
        self.assertEqual(1, len(response.data['results']))

    def test_list_allocations_unauthenticated(self):
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_allocations_negative(self):
        self.client.force_authenticate(user=self.user)
        factories.AllocationFactory.create(contact_email='other@example.com')
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))

    def test_list_allocations_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.AllocationFactory.create(contact_email='other@example.com')
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data['results']))

    def test_filter_contact_email(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.AllocationFactory.create(contact_email='other@example.com')
        response = self.client.get(
            '/rest_api/allocations/?contact_email=other@example.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))

    def test_filter_national(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.AllocationFactory.create(national=True)
        response = self.client.get('/rest_api/allocations/?national=True')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        response = self.client.get('/rest_api/allocations/?national=False')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))

    def test_filter_allocation_home_national(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.AllocationFactory.create(national=True)
        response = self.client.get(
            '/rest_api/allocations/?allocation_home=national')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertEqual(response.data['results'][0]['allocation_home'],
                         'national')
        self.assertEqual(response.data['results'][0]['national'], True)

    def test_filter_allocation_home_unassigned(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.AllocationFactory.create(national=False,
                                           associated_site=None)
        response = self.client.get(
            '/rest_api/allocations/?allocation_home=unassigned')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertEqual(response.data['results'][0]['allocation_home'],
                         'unassigned')
        self.assertEqual(response.data['results'][0]['national'], False)
        self.assertIsNone(response.data['results'][0]['associated_site'])

    def test_filter_allocation_home_local(self):
        self.client.force_authenticate(user=self.admin_user)
        current_site = self.allocation.associated_site.name
        factories.AllocationFactory.create(national=False,
                                           associated_site=None)
        response = self.client.get(
            '/rest_api/allocations/?allocation_home=%s' % current_site)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertEqual(response.data['results'][0]['allocation_home'],
                         current_site)
        self.assertEqual(response.data['results'][0]['national'], False)
        self.assertEqual(response.data['results'][0]['associated_site'],
                         current_site)

    def test_filter_associated_site_name(self):
        self.client.force_authenticate(user=self.admin_user)
        current_site = self.allocation.associated_site.name
        factories.AllocationFactory.create(national=False,
                                           associated_site=None)
        response = self.client.get(
            '/rest_api/allocations/?associated_site=%s' % current_site)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertEqual(response.data['results'][0]['allocation_home'],
                         current_site)
        self.assertEqual(response.data['results'][0]['national'], False)
        self.assertEqual(response.data['results'][0]['associated_site'],
                         current_site)

        response = self.client.get(
            '/rest_api/allocations/?associated_site=kanmantoo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data['results']))

    def test_get_allocation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/allocations/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, response.data['id'])
        for field in ['notes', 'status_explanation']:
            self.assertNotIn(field, response.data.keys())
        site = response.data['associated_site']
        self.assertEqual(response.data['national'], False)
        self.assertEqual(response.data['allocation_home'], site)
        self.assertEqual(response.data['allocation_home_display'], site)

    def test_get_allocation_unauthenticated(self):
        response = self.client.get('/rest_api/allocations/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        public_fields = ['id', 'project_name', 'project_description',
                         'modified_time', 'submit_date', 'start_date',
                         'end_date', 'field_of_research_1',
                         'field_of_research_2', 'field_of_research_3',
                         'for_percentage_1', 'for_percentage_2',
                         'for_percentage_3', 'quotas']
        self.assertEqual(public_fields, list(response.data.keys()))

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

    def test_update_national(self):
        # Checking my assumptions ....
        self.assertFalse(self.allocation.national)

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            '/rest_api/allocations/1/',
            {'national': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id)
        self.assertTrue(allocation.national)

    def test_update_national_as_user(self):
        # Checking my assumptions ....
        self.assertFalse(self.allocation.national)

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            '/rest_api/allocations/1/',
            {'national': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # It returns 200 but value doesn't change
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id)
        self.assertFalse(allocation.national)

    def test_update_associated_site(self):
        current_site = self.allocation.associated_site.name
        new_site = 'monash' if current_site != 'monash' else 'qcif'

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            '/rest_api/allocations/1/',
            {'associated_site': new_site})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id)
        self.assertEqual(allocation.associated_site.name, new_site)

    def test_update_associated_site_as_user(self):
        current_site = self.allocation.associated_site.name
        new_site = 'monash' if current_site != 'monash' else 'qcif'

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            '/rest_api/allocations/1/',
            {'associated_site': new_site})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_allocation_home_local(self):
        self.client.force_authenticate(user=self.admin_user)
        current_site = self.allocation.associated_site.name
        new_site = 'monash' if current_site != 'monash' else 'qcif'
        response = self.client.patch(
            '/rest_api/allocations/1/',
            {'allocation_home': new_site})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id)
        self.assertEqual(allocation.associated_site.name, new_site)
        self.assertFalse(allocation.national)

    def test_update_allocation_home_national(self):
        self.client.force_authenticate(user=self.admin_user)
        current_site = self.allocation.associated_site.name
        response = self.client.patch(
            '/rest_api/allocations/1/',
            {'allocation_home': 'national'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id)
        self.assertEqual(allocation.associated_site.name, current_site)
        self.assertTrue(allocation.national)

    def test_update_allocation_home_unassigned(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            '/rest_api/allocations/1/',
            {'allocation_home': 'unassigned'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id)
        self.assertIsNone(allocation.associated_site)
        self.assertFalse(allocation.national)

    def test_update_allocation_dates(self):
        self.client.force_authenticate(user=self.admin_user)
        start_date = datetime.date(2019, 4, 2)
        end_date = datetime.date(2019, 5, 2)
        response = self.client.patch(
            '/rest_api/allocations/1/',
            {'start_date': start_date.strftime('%Y-%m-%d'),
             'end_date': end_date.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id)
        self.assertEqual(start_date, allocation.start_date)
        self.assertEqual(end_date, allocation.end_date)

    def test_update_allocation_dates_user(self):
        self.client.force_authenticate(user=self.user)
        start_date = datetime.date(2019, 4, 3)
        end_date = datetime.date(2019, 5, 3)
        response = self.client.patch(
            '/rest_api/allocations/1/',
            {'start_date': start_date.strftime('%Y-%m-%d'),
             'end_date': end_date.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id)
        self.assertIsNone(allocation.start_date)
        self.assertIsNone(allocation.end_date)

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
        self.client.force_authenticate(user=self.admin_user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        allocation = models.AllocationRequest.objects.get(
            project_name='test-project')
        self.assertEqual(self.admin_user.token.project['id'],
                         allocation.created_by)
        self.assertEqual('test-project', response.data['project_name'])
        self.assertEqual(self.admin_user.username,
                         response.data['contact_email'])
        self.assertIsNone(response.data['associated_site'])
        self.assertEqual(response.data['allocation_home'], 'unassigned')
        self.assertFalse(response.data['national'])
        self.assertEqual(models.AllocationRequest.SUBMITTED,
                         response.data['status'])

    def test_create_as_user(self):
        self.client.force_authenticate(user=self.user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        allocation = models.AllocationRequest.objects.get(
            project_name='test-project')
        self.assertEqual(self.user.token.project['id'], allocation.created_by)
        self.assertEqual('test-project', response.data['project_name'])
        self.assertEqual(self.user.username, response.data['contact_email'])
        self.assertIsNone(response.data['associated_site'])
        self.assertEqual(response.data['allocation_home'], 'unassigned')
        self.assertFalse(response.data['national'])
        self.assertEqual(models.AllocationRequest.SUBMITTED,
                         response.data['status'])

    def test_create_as_with_no_site(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'national': False,
                'associated_site': ''}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        allocation = models.AllocationRequest.objects.get(
            project_name='test-project')
        self.assertEqual(self.admin_user.token.project['id'],
                         allocation.created_by)
        self.assertEqual('test-project', response.data['project_name'])
        self.assertEqual(self.admin_user.username,
                         response.data['contact_email'])
        self.assertIsNone(response.data['associated_site'])
        self.assertEqual(response.data['allocation_home'], 'unassigned')
        self.assertFalse(response.data['national'])
        self.assertEqual(models.AllocationRequest.SUBMITTED,
                         response.data['status'])

    def test_create_as_user_with_no_site(self):
        # This is apparently indistinguishable from the case where the
        # 'national' and 'associated_site' fields are omitted.  Check
        # that 'national' and `associate_site` are indeed set to their
        # default values.
        self.client.force_authenticate(user=self.user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'national': False,
                'associated_site': ''}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['national'])
        self.assertIsNone(response.data['associated_site'])

    def test_create_as_user_with_national(self):
        # This is apparently indistinguishable from the case where the
        # 'national' and 'associated_site' fields are omitted.  Check
        # that 'national' and `associate_site` are indeed set to their
        # default values.
        self.client.force_authenticate(user=self.user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'national': True,
                'associated_site': ''}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['national'])
        self.assertIsNone(response.data['associated_site'])

    def test_create_with_associated_site(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'national': False,
                'associated_site': 'qcif'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        allocation = models.AllocationRequest.objects.get(
            project_name='test-project')
        self.assertEqual(self.admin_user.token.project['id'],
                         allocation.created_by)
        self.assertEqual('test-project', response.data['project_name'])
        self.assertEqual(self.admin_user.username,
                         response.data['contact_email'])
        self.assertEqual(response.data['associated_site'], 'qcif')
        self.assertEqual(response.data['allocation_home'], 'qcif')
        self.assertFalse(response.data['national'])
        self.assertEqual(models.AllocationRequest.SUBMITTED,
                         response.data['status'])

    def test_create_with_associated_site_as_user(self):
        self.client.force_authenticate(user=self.user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'national': False,
                'associated_site': 'qcif'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_override_contact_email(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'contact_email': 'test_override@example.com'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        allocation = models.AllocationRequest.objects.get(
            project_name='test-project')
        self.assertEqual(self.admin_user.token.project['id'],
                         allocation.created_by)
        self.assertEqual('test-project', response.data['project_name'])
        self.assertEqual('test_override@example.com',
                         response.data['contact_email'])
        self.assertEqual(models.AllocationRequest.SUBMITTED,
                         response.data['status'])

    def test_create_bad_site(self):
        self.client.force_authenticate(user=self.user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'national': False,
                'associated_site': 'Bogus'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['associated_site'][0]),
                         "Site 'Bogus' does not exist")

    def test_create_alloc_home(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'allocation_home': 'qcif'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['allocation_home'], 'qcif')
        self.assertEqual(response.data['associated_site'], 'qcif')
        self.assertFalse(response.data['national'])
        self.assertEqual(models.AllocationRequest.SUBMITTED,
                         response.data['status'])

    def test_create_alloc_home_national(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'allocation_home': 'national'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['allocation_home'], 'national')
        self.assertEqual(response.data['associated_site'], None)
        self.assertTrue(response.data['national'])
        self.assertEqual(models.AllocationRequest.SUBMITTED,
                         response.data['status'])

    def test_create_alloc_home_unassigned(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'allocation_home': 'unassigned'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['allocation_home'], 'unassigned')
        self.assertEqual(response.data['associated_site'], None)
        self.assertFalse(response.data['national'])
        self.assertEqual(models.AllocationRequest.SUBMITTED,
                         response.data['status'])

    def test_create_alloc_home_as_user(self):
        self.client.force_authenticate(user=self.user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'allocation_home': 'qcif'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_bogus_alloc_home(self):
        self.client.force_authenticate(user=self.user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'allocation_home': 'Bogus'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['allocation_home'][0]),
                         "Site 'Bogus' does not exist")

    def test_create_bogus_alloc_home2(self):
        self.client.force_authenticate(user=self.user)
        for bogus in ['national', 'unassigned']:
            data = {'project_name': 'test-project',
                    'project_description': 'project for testing',
                    'start_date': '2000-01-01',
                    'use_case': 'for testing',
                    'allocation_home': bogus}
            response = self.client.post('/rest_api/allocations/', data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_alloc_home_conflict(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'national': False,
                'associated_site': 'qcif',
                'allocation_home': 'qcif'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data[0]),
                         "Cannot use 'allocation_home' with 'national' "
                         "or 'associated_site'")

    def test_create_duplicate_project_name(self):
        self.client.force_authenticate(user=self.user)
        factories.AllocationFactory.create(project_name='test-project')
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing'}
        response = self.client.post('/rest_api/allocations/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['project_name'][0]),
                         "Project name already exists")

    def test_create_unauthenticated(self):
        data = {'project_name': 'test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
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

    def test_approve_no_site(self):
        self.client.force_authenticate(user=self.approver_user)
        allocation = factories.AllocationFactory.create(
            associated_site=None)
        response = self.client.post(
            '/rest_api/allocations/%s/approve/' % allocation.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'],
                         "The associated_site attribute must be set "
                         "before approving")

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
        # Check my assumptions
        self.assertEqual(models.AllocationRequest.objects.filter(
            parent_request__id=self.allocation.id).count(),
                         0)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/rest_api/allocations/1/delete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.AllocationRequest.DELETED,
                         response.data['status'])
        # Check that a history record has been created
        self.assertEqual(models.AllocationRequest.objects.filter(
            parent_request__id=self.allocation.id).count(),
                         1)

    def test_delete_deleted(self):
        self.client.force_authenticate(user=self.admin_user)
        self.allocation.status = models.AllocationRequest.DELETED
        self.allocation.save()
        response = self.client.post('/rest_api/allocations/%s/delete/' %
                                    self.allocation.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that no history record was created
        self.assertEqual(models.AllocationRequest.objects.filter(
            parent_request__id=self.allocation.id).count(),
                         0)

    def test_delete_historic(self):
        self.client.force_authenticate(user=self.admin_user)
        # Kludge ... a history record is one with a parent
        self.allocation.parent_request = self.allocation
        self.allocation.save()
        response = self.client.post('/rest_api/allocations/%s/delete/' %
                                    self.allocation.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_invalid_role(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest_api/allocations/1/delete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/rest_api/allocations/1/')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
