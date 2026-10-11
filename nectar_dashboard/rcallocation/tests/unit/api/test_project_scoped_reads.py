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
from nectar_dashboard.rcallocation.tests import utils


@mock.patch(
    'nectar_dashboard.rcallocation.notifier.FreshdeskNotifier',
    new=base.FAKE_FD_NOTIFIER_CLASS,
)
@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class ProjectScopedReadTests(base.AllocationAPITest):
    """A project member may read the approved allocation of the project
    their token is scoped to, not only the requests they are the contact
    for. The new dashboard reads the SU budget and quotas this way with the
    user's own token.
    """

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # proj2's approved allocation, whose contact is somebody else.
        self.project_allocation = factories.AllocationFactory.create(
            contact_email='someone-else@example.com',
            project_id='idproj2',
            project_name='proj2',
            status=models.AllocationRequest.APPROVED,
        )
        # A pending request for the same project is still private.
        self.pending = factories.AllocationFactory.create(
            contact_email='someone-else@example.com',
            project_id='idproj2',
            project_name='proj2',
            status=models.AllocationRequest.SUBMITTED,
        )
        self.member = self.user2  # scoped to idproj2, not the contact
        self.outsider = self.user  # scoped to idproj1
        self.contact = utils.get_user(
            id='contact',
            username='someone-else@example.com',
            project_name='unrelated',
        )

    def _ids(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return {a['id'] for a in response.data['results']}

    def test_member_sees_own_project_approved_allocation(self):
        self.client.force_authenticate(user=self.member)
        ids = self._ids(self.client.get('/rest_api/allocations/'))
        self.assertIn(self.project_allocation.id, ids)
        self.assertNotIn(self.pending.id, ids)
        self.assertNotIn(self.allocation.id, ids)

    def test_member_can_filter_by_project_id(self):
        self.client.force_authenticate(user=self.member)
        ids = self._ids(
            self.client.get(
                '/rest_api/allocations/?project_id=idproj2&status=A'
            )
        )
        self.assertEqual({self.project_allocation.id}, ids)

    def test_member_can_retrieve_it(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get(
            f'/rest_api/allocations/{self.project_allocation.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_id'], 'idproj2')

    def test_other_project_member_cannot_see_it(self):
        self.client.force_authenticate(user=self.outsider)
        ids = self._ids(self.client.get('/rest_api/allocations/'))
        self.assertNotIn(self.project_allocation.id, ids)
        self.assertNotIn(self.pending.id, ids)
        # Their own request is still there.
        self.assertIn(self.allocation.id, ids)
        response = self.client.get(
            f'/rest_api/allocations/{self.project_allocation.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_contact_still_sees_pending_requests(self):
        self.client.force_authenticate(user=self.contact)
        ids = self._ids(self.client.get('/rest_api/allocations/'))
        self.assertEqual({self.project_allocation.id, self.pending.id}, ids)

    def test_member_cannot_update_project_allocation(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.patch(
            f'/rest_api/allocations/{self.project_allocation.id}/',
            {'use_case': 'changed'},
            format='json',
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )

    def test_quotas_follow_allocation_visibility(self):
        quota = models.Quota.objects.filter(
            group__allocation=self.project_allocation
        ).first()
        self.assertIsNotNone(quota, "factory should create quotas")
        pending_quota = models.Quota.objects.filter(
            group__allocation=self.pending
        ).first()

        self.client.force_authenticate(user=self.member)
        response = self.client.get('/rest_api/quotas/')
        ids = self._ids(response)
        self.assertIn(quota.id, ids)
        self.assertNotIn(pending_quota.id, ids)

        self.client.force_authenticate(user=self.outsider)
        ids = self._ids(self.client.get('/rest_api/quotas/'))
        self.assertNotIn(quota.id, ids)
