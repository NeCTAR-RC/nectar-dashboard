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

from django.contrib.auth import models as auth_models
from django import test

from rest_framework import status

from nectar_dashboard.rcallocation.api import auth
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import utils


@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class ScopedRoleCheckTest(test.SimpleTestCase):
    """has_roles and friends must match roles by token scope.

    Keystone role inference hands every project user implied roles
    (member implies reader), so the system-scope role names must never
    match a project-scoped token, and vice versa.
    """

    def test_project_scoped_system_role_names_grant_nothing(self):
        user = utils.get_user(roles=['member', 'reader'])
        self.assertFalse(auth.is_read_admin(user))
        self.assertFalse(auth.is_write_admin(user))

    def test_system_scoped_project_role_names_grant_nothing(self):
        user = utils.get_system_user(roles=['read_only'])
        self.assertFalse(auth.is_read_admin(user))
        self.assertFalse(auth.is_write_admin(user))

    def test_system_scoped_reader(self):
        user = utils.get_system_user(roles=['reader'])
        self.assertTrue(auth.is_read_admin(user))
        self.assertFalse(auth.is_write_admin(user))

    def test_system_scoped_admin(self):
        # A system admin assignment implies member and reader
        user = utils.get_system_user(roles=['admin', 'member', 'reader'])
        self.assertTrue(auth.is_read_admin(user))
        self.assertTrue(auth.is_write_admin(user))

    def test_project_scoped_admin_unchanged(self):
        user = utils.get_user(roles=['admin'])
        self.assertTrue(auth.is_read_admin(user))
        self.assertTrue(auth.is_write_admin(user))

    def test_unauthenticated(self):
        user = auth_models.AnonymousUser()
        self.assertFalse(auth.is_read_admin(user))
        self.assertFalse(auth.is_write_admin(user))


@mock.patch(
    'nectar_dashboard.rcallocation.notifier.FreshdeskNotifier',
    new=base.FAKE_FD_NOTIFIER_CLASS,
)
@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class SystemScopeAllocationTests(base.AllocationAPITest):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.system_admin = utils.get_system_user(
            id='sysadmin',
            username='system-admin',
            roles=['admin', 'member', 'reader'],
        )
        self.system_reader = utils.get_system_user(
            id='sysreader', username='system-reader', roles=['reader']
        )
        self.system_approver = utils.get_system_user(
            id='sysapprover',
            username='system-approver',
            roles=['allocationapprover'],
        )
        self.system_member = utils.get_system_user(
            id='sysmember', username='system-member', roles=['member']
        )

    def test_list_allocations_system_admin(self):
        self.client.force_authenticate(user=self.system_admin)
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        # Admin serializer exposes admin-only fields
        self.assertIn('notes', response.data['results'][0])

    def test_list_allocations_system_reader(self):
        self.client.force_authenticate(user=self.system_reader)
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertIn('notes', response.data['results'][0])

    def test_list_allocations_system_member(self):
        # No matching system role: sees only allocations it owns
        self.client.force_authenticate(user=self.system_member)
        response = self.client.get('/rest_api/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data['results']))

    def test_get_allocation_system_member(self):
        self.client.force_authenticate(user=self.system_member)
        response = self.client.get(
            f'/rest_api/allocations/{self.allocation.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_allocation_system_admin(self):
        self.client.force_authenticate(user=self.system_admin)
        response = self.client.patch(
            f'/rest_api/allocations/{self.allocation.id}/',
            {'use_case': 'test-update'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id
        )
        self.assertEqual('test-update', allocation.use_case)

    def test_update_allocation_admin_field_system_admin(self):
        self.client.force_authenticate(user=self.system_admin)
        response = self.client.patch(
            f'/rest_api/allocations/{self.allocation.id}/',
            {'national': True},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id
        )
        self.assertTrue(allocation.national)

    def test_update_allocation_admin_field_system_member(self):
        self.client.force_authenticate(user=self.system_member)
        response = self.client.patch(
            f'/rest_api/allocations/{self.allocation.id}/',
            {'national': True},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_approve_system_approver(self):
        self.client.force_authenticate(user=self.system_approver)
        response = self.client.post(
            f'/rest_api/allocations/{self.allocation.id}/approve/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            models.AllocationRequest.APPROVED, response.data['status']
        )
        allocation = models.AllocationRequest.objects.get(
            id=self.allocation.id
        )
        self.assertEqual(
            self.system_approver.username, allocation.approver_email
        )

    def test_approve_system_admin(self):
        # As at project scope, the admin role alone cannot approve
        self.client.force_authenticate(user=self.system_admin)
        response = self.client.post(
            f'/rest_api/allocations/{self.allocation.id}/approve/'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_system_reader(self):
        self.client.force_authenticate(user=self.system_reader)
        response = self.client.post(
            f'/rest_api/allocations/{self.allocation.id}/approve/'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_system_admin(self):
        self.client.force_authenticate(user=self.system_admin)
        response = self.client.post(
            f'/rest_api/allocations/{self.allocation.id}/delete/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            models.AllocationRequest.DELETED, response.data['status']
        )

    def test_delete_system_reader(self):
        self.client.force_authenticate(user=self.system_reader)
        response = self.client.post(
            f'/rest_api/allocations/{self.allocation.id}/delete/'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_system_admin(self):
        self.client.force_authenticate(user=self.system_admin)
        response = self.client.post(
            '/rest_api/allocations/',
            {
                'project_name': 'system-test-project',
                'project_description': 'project for testing',
                'start_date': '2000-01-01',
                'use_case': 'for testing',
                'usage_types': ['Other'],
                'supported_organisations': ['https://ror.org/12345678'],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        allocation = models.AllocationRequest.objects.get(
            project_name='system-test-project'
        )
        self.assertEqual(self.system_admin.id, allocation.created_by)
        self.assertEqual(
            self.system_admin.username, response.data['contact_email']
        )
