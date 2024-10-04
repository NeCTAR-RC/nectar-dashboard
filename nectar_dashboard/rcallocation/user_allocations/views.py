import logging

from django.db.models import Q

from nectar_dashboard.api import manuka
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.user_allocations import forms
from nectar_dashboard.rcallocation.user_allocations import tables
from nectar_dashboard.rcallocation import utils
from nectar_dashboard.rcallocation import views


LOG = logging.getLogger('nectar_dashboard.rcallocation')


class BaseAllocationUpdateView(views.BaseAllocationView):
    page_title = 'Update'
    editor_attr = 'contact_email'

    def test_func(self):
        return check_tm_or_alloc_admin(self.request, self.get_object())


class RestrictedAllocationsEditView(BaseAllocationUpdateView):
    page_title = 'Edit Allocation Request'
    template_name = "rcallocation/allocationrequest_user_update.html"
    model = models.AllocationRequest
    form_class = forms.UserAllocationRequestForm
    success_url = "../../"

    def get_initial(self):
        initial = super().get_initial()
        if self.object.can_be_amended():
            initial['direct_access_user_past_year'] = (
                self.object.direct_access_user_estimate
            )
            initial['active_service_count'] = (
                self.object.estimated_service_count
            )
            initial['service_active_users_past_year'] = (
                self.object.estimated_service_active_users
            )
        return initial


class RestrictedAllocationsDetailsView(views.AllocationDetailView):
    template_name = "rcallocation/allocationrequest_user_detail.html"
    page_title = 'View Allocation Request'

    def test_func(self):
        return check_tm_or_alloc_admin(self.request, self.get_object())


def check_tm_or_alloc_admin(request, object):
    if object:
        if object.is_history():
            return False
        if (
            not object.contact_email == request.user.username
            and not utils.user_is_allocation_admin(request.user)
        ):
            managed_projects = get_managed_projects(request)
            if object.project_id not in managed_projects:
                return False
    return True


def get_managed_projects(request):
    client = manuka.manukaclient(request)
    return client.users.projects(request.user.id, 'TenantManager')


class UserAllocationsListView(views.BaseAllocationsListView):
    """A simple paginated view of the allocation requests, ordered by
    status. Later we should perhaps add sortable columns, filterable
    by status?
    """

    context_object_name = "allocation_list"
    table_class = tables.UserAllocationListTable
    template_name = 'rcallocation/allocationrequest_user_list.html'
    page_title = 'My Requests'

    def get_data(self):
        contact_email = self.request.user.username
        managed_projects = get_managed_projects(self.request)
        return (
            models.AllocationRequest.objects.filter(parent_request=None)
            .filter(
                Q(project_id__in=list(managed_projects))
                | Q(contact_email__exact=contact_email)
            )
            .order_by('status')
        )

    def test_func(self):
        # Any user is allowed to list allocations.  The filter should
        # limit what they see.
        return True
