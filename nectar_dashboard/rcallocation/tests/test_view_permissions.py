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

from django.contrib.auth import mixins
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from openstack_auth import utils as auth_utils

from nectar_dashboard.rcallocation.allocation import views as alloc_views
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.request import views as request_views
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories
from nectar_dashboard.rcallocation.user_allocations import views as ua_views
from nectar_dashboard.rcallocation import utils
from nectar_dashboard.rcallocation import views


MANAGED_PROJECT_ID = 'managed-project-id'
OTHER_CONTACT = 'someone-else@example.com'

EDIT_URLS = (
    'horizon:allocation:user_requests:edit_request',
    'horizon:allocation:user_requests:edit_change_request',
)


def mock_get_user(self):
    return mock.Mock()


def mock_manuka(managed_projects):
    """Patch the manuka client used by get_managed_projects()."""
    client = mock.Mock()
    client.users.projects.return_value = managed_projects
    return mock.patch(
        'nectar_dashboard.api.manuka.manukaclient', return_value=client
    )


class DispatchOrderTestCase(base.BaseTestCase):
    """UserPassesTestMixin.dispatch must be the dispatch that runs, or
    test_func() is silently skipped.
    """

    def test_access_mixin_dispatch_runs_first(self):
        for view_class in (
            views.AllocationDetailView,
            views.BaseAllocationsListView,
            views.AllocationHistoryView,
            views.BaseAllocationView,
            alloc_views.PendingAllocationsListView,
            alloc_views.AllocationUpdateView,
            alloc_views.AllocationNotesEdit,
            alloc_views.AllocationApproveView,
            alloc_views.AllocationRejectView,
            request_views.AllocationCreateView,
            ua_views.BaseAllocationUpdateView,
            ua_views.RestrictedAllocationsEditView,
            ua_views.RestrictedAllocationsDetailsView,
            ua_views.UserAllocationsListView,
        ):
            self.assertIs(
                view_class.dispatch,
                mixins.UserPassesTestMixin.dispatch,
                msg=f"{view_class.__name__} bypasses test_func()",
            )


@mock.patch(
    'nectar_dashboard.rcallocation.views.BaseAllocationView.get_user',
    new=mock_get_user,
)
@mock.patch(
    'nectar_dashboard.rcallocation.notifier.FreshdeskNotifier',
    new=base.FAKE_FD_NOTIFIER_CLASS,
)
class UserEditPermissionTestCase(base.BaseTestCase):
    """Access rules for the user-facing edit and amend views."""

    def setUp(self):
        super().setUp()
        self.allocation = factories.AllocationFactory.create(
            contact_email=OTHER_CONTACT,
            project_id=MANAGED_PROJECT_ID,
            status=models.AllocationRequest.APPROVED,
        )

    def _assert_unchanged(self, allocation):
        self.assertFalse(
            models.AllocationRequest.objects.filter(
                parent_request=allocation
            ).exists(),
            msg="a history record was created",
        )

    def test_unrelated_user_denied(self):
        with mock_manuka([]):
            for name in EDIT_URLS:
                url = reverse(name, args=(self.allocation.id,))
                response = self.client.get(url)
                self.assertStatusCode(response, 403)
                response = self.client.post(url, {'ignore_warnings': True})
                self.assertStatusCode(response, 403)
        self._assert_unchanged(self.allocation)

    def test_unrelated_user_denied_with_valid_form(self):
        with mock_manuka(['some-other-project']):
            _, form = common.request_allocation(
                user=self.user, model=self.allocation, amending=True
            )
            form['ignore_warnings'] = True
            url = reverse(
                'horizon:allocation:user_requests:edit_change_request',
                args=(self.allocation.id,),
            )
            response = self.client.post(url, form)
        self.assertStatusCode(response, 403)
        self._assert_unchanged(self.allocation)

    def test_contact_allowed(self):
        self.allocation.contact_email = self.user.name
        self.allocation.save()
        with mock_manuka([]) as manuka:
            for name in EDIT_URLS:
                response = self.client.get(
                    reverse(name, args=(self.allocation.id,))
                )
                self.assertStatusCode(response, 200)
            # The contact check short-circuits the TenantManager lookup
            manuka.assert_not_called()

    def test_tenant_manager_allowed(self):
        with mock_manuka([MANAGED_PROJECT_ID]):
            for name in EDIT_URLS:
                response = self.client.get(
                    reverse(name, args=(self.allocation.id,))
                )
                self.assertStatusCode(response, 200)

    def test_tenant_manager_can_submit(self):
        with mock_manuka([MANAGED_PROJECT_ID]):
            _, form = common.request_allocation(
                user=self.user, model=self.allocation, amending=True
            )
            form['ignore_warnings'] = True
            response = self.client.post(
                reverse(
                    'horizon:allocation:user_requests:edit_change_request',
                    args=(self.allocation.id,),
                ),
                form,
            )
        self.assertStatusCode(response, 302)
        self.assertTrue(
            models.AllocationRequest.objects.filter(
                parent_request=self.allocation
            ).exists()
        )

    def test_history_record_denied_for_contact(self):
        self.allocation.contact_email = self.user.name
        self.allocation.save()
        history = utils.copy_allocation(self.allocation)
        with mock_manuka([MANAGED_PROJECT_ID]):
            for name in EDIT_URLS:
                url = reverse(name, args=(history.id,))
                response = self.client.get(url)
                self.assertStatusCode(response, 403)
                response = self.client.post(url, {'ignore_warnings': True})
                self.assertStatusCode(response, 403)


@mock.patch(
    'nectar_dashboard.rcallocation.views.BaseAllocationView.get_user',
    new=mock_get_user,
)
class AdminUserEditPermissionTestCase(base.BaseApproverTestCase):
    """An allocation admin may use the user-facing edit views."""

    def test_allocation_admin_allowed(self):
        allocation = factories.AllocationFactory.create(
            contact_email=OTHER_CONTACT,
            project_id=MANAGED_PROJECT_ID,
            status=models.AllocationRequest.APPROVED,
        )
        with mock_manuka([]) as manuka:
            for name in EDIT_URLS:
                response = self.client.get(
                    reverse(name, args=(allocation.id,))
                )
                self.assertStatusCode(response, 200)
            manuka.assert_not_called()

    def test_allocation_admin_denied_history(self):
        allocation = factories.AllocationFactory.create(
            contact_email=OTHER_CONTACT,
            status=models.AllocationRequest.APPROVED,
        )
        history = utils.copy_allocation(allocation)
        with mock_manuka([]):
            for name in EDIT_URLS:
                response = self.client.get(reverse(name, args=(history.id,)))
                self.assertStatusCode(response, 403)


class AdminViewDirectPermissionTestCase(base.BaseTestCase):
    """The admin views must enforce test_func() themselves, without
    relying on the Horizon panel permission.
    """

    ADMIN_VIEWS = (
        alloc_views.AllocationUpdateView,
        alloc_views.AllocationApproveView,
        alloc_views.AllocationRejectView,
        alloc_views.AllocationNotesEdit,
    )

    def setUp(self):
        super().setUp()
        self.allocation = factories.AllocationFactory.create(
            contact_email=self.user.name,
            status=models.AllocationRequest.SUBMITTED,
        )

    def _call(self, view_class, method):
        request = getattr(self.factory, method)('/', {})
        request.user = auth_utils.get_user(request)
        self.assertFalse(utils.user_is_allocation_admin(request.user))
        return view_class.as_view()(request, pk=self.allocation.id)

    def test_non_admin_denied(self):
        for view_class in self.ADMIN_VIEWS:
            for method in ('get', 'post'):
                with self.subTest(view=view_class.__name__, method=method):
                    self.assertRaises(
                        PermissionDenied, self._call, view_class, method
                    )
        self.assertFalse(
            models.AllocationRequest.objects.filter(
                parent_request=self.allocation
            ).exists()
        )


@mock.patch(
    'nectar_dashboard.rcallocation.views.BaseAllocationView.get_user',
    new=mock_get_user,
)
@mock.patch(
    'nectar_dashboard.rcallocation.notifier.FreshdeskNotifier',
    new=base.FAKE_FD_NOTIFIER_CLASS,
)
class CreatePermissionTestCase(base.BaseTestCase):
    def test_normal_user_can_create(self):
        url = reverse('horizon:allocation:request:request')
        response = self.client.get(url)
        self.assertStatusCode(response, 200)

        _, form = common.request_allocation(user=self.user)
        form['ignore_warnings'] = True
        response = self.client.post(url, form)
        self.assertStatusCode(response, 302)
        self.assertTrue(
            models.AllocationRequest.objects.filter(
                project_description=form['project_description'],
                contact_email=self.user.name,
            ).exists()
        )
