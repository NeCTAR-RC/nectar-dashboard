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

"""The allocation action views only act on allocations in the states
for which the matching action is offered (NECTAR-17320).
"""

from unittest import mock

from django.urls import reverse

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories


AR = models.AllocationRequest
ALL_STATUSES = (
    AR.NEW,
    AR.SUBMITTED,
    AR.APPROVED,
    AR.DECLINED,
    AR.UPDATE_PENDING,
    AR.UPDATE_DECLINED,
    AR.DELETED,
)

# URL name -> the statuses in which the view acts on an allocation
USER_VIEW_STATES = {
    'horizon:allocation:user_requests:edit_request': (
        AR.NEW,
        AR.SUBMITTED,
        AR.DECLINED,
    ),
    'horizon:allocation:user_requests:edit_change_request': (
        AR.APPROVED,
        AR.UPDATE_PENDING,
        AR.UPDATE_DECLINED,
    ),
}

ADMIN_VIEW_STATES = {
    'horizon:allocation:requests:edit_request': (
        AR.NEW,
        AR.SUBMITTED,
        AR.UPDATE_PENDING,
        AR.UPDATE_DECLINED,
    ),
    'horizon:allocation:requests:approve_request': (
        AR.NEW,
        AR.SUBMITTED,
        AR.UPDATE_PENDING,
    ),
    'horizon:allocation:requests:approve_change_request': (
        AR.NEW,
        AR.SUBMITTED,
        AR.UPDATE_PENDING,
    ),
    'horizon:allocation:requests:reject_request': (
        AR.NEW,
        AR.SUBMITTED,
        AR.UPDATE_PENDING,
    ),
}


def mock_get_user(self):
    return mock.Mock()


class StateTestMixin:
    def _assert_states(self, view_states):
        for name, allowed in view_states.items():
            for status in ALL_STATUSES:
                with self.subTest(view=name, status=status):
                    allocation = factories.AllocationFactory.create(
                        contact_email=self.user.name, status=status
                    )
                    url = reverse(name, args=(allocation.id,))
                    response = self.client.get(url)
                    if status in allowed:
                        self.assertStatusCode(response, 200)
                        continue
                    self.assertStatusCode(response, 400)
                    response = self.client.post(url, {'ignore_warnings': True})
                    self.assertStatusCode(response, 400)
                    allocation.refresh_from_db()
                    self.assertEqual(status, allocation.status)
                    self.assertFalse(
                        AR.objects.filter(parent_request=allocation).exists(),
                        msg="a history record was created",
                    )


@mock.patch(
    'nectar_dashboard.rcallocation.views.BaseAllocationView.get_user',
    new=mock_get_user,
)
class UserViewStateTestCase(StateTestMixin, base.BaseTestCase):
    def test_user_view_states(self):
        self._assert_states(USER_VIEW_STATES)

    def test_unmanaged_not_editable(self):
        for name, allowed in USER_VIEW_STATES.items():
            allocation = factories.AllocationFactory.create(
                contact_email=self.user.name, status=allowed[0], managed=False
            )
            response = self.client.get(reverse(name, args=(allocation.id,)))
            self.assertStatusCode(response, 400)


@mock.patch(
    'nectar_dashboard.rcallocation.views.BaseAllocationView.get_user',
    new=mock_get_user,
)
class AdminViewStateTestCase(StateTestMixin, base.BaseApproverTestCase):
    def test_admin_view_states(self):
        self._assert_states(ADMIN_VIEW_STATES)

    def test_guard_messages(self):
        approved = factories.AllocationFactory.create(status=AR.APPROVED)
        declined = factories.AllocationFactory.create(
            status=AR.UPDATE_DECLINED
        )
        for name, allocation, message in (
            ('approve_request', approved, b'Allocation already approved'),
            ('approve_change_request', declined, b'not awaiting approval'),
            ('reject_request', declined, b'Allocation already declined'),
            ('reject_request', approved, b'not awaiting approval'),
        ):
            url = reverse(
                f'horizon:allocation:requests:{name}', args=(allocation.id,)
            )
            self.assertIn(message, self.client.get(url).content)

    def test_declined_change_offers_no_approval_actions(self):
        allocation = factories.AllocationFactory.create(
            status=AR.UPDATE_DECLINED
        )
        url = reverse(
            'horizon:allocation:requests:allocation_view',
            args=(allocation.id,),
        )
        response = self.client.get(url)
        self.assertStatusCode(response, 200)
        self.assertNotContains(response, 'Approve changes')
        self.assertNotContains(response, 'Decline changes')

    def test_pending_change_offers_approval_actions(self):
        allocation = factories.AllocationFactory.create(
            status=AR.UPDATE_PENDING
        )
        url = reverse(
            'horizon:allocation:requests:allocation_view',
            args=(allocation.id,),
        )
        response = self.client.get(url)
        self.assertContains(response, 'Approve changes')
        self.assertContains(response, 'Decline changes')
