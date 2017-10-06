import logging
from collections import defaultdict

from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied

from horizon.utils.memoized import memoized
from openstack_dashboard.api import keystone

from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import views

from .forms import UserAllocationRequestForm
from .tables import UserAllocationListTable

LOG = logging.getLogger('nectar_dashboard.rcallocation')


class BaseAllocationUpdateView(views.BaseAllocationView):
    page_title = 'Update'
    editor_attr = 'contact_email'
    formset_quota_class = inlineformset_factory(
        models.AllocationRequest, models.Quota, form=forms.QuotaForm, extra=0)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_archived():
            raise PermissionDenied()
        if not self.object.contact_email == request.user.username:
            managed_projects = get_managed_projects(self.request)
            if self.object.project_id not in managed_projects and \
               not views.user_is_allocation_admin(request.user):
                raise PermissionDenied()
        return super(BaseAllocationUpdateView, self) \
            .get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_archived():
            raise PermissionDenied()
        if not self.object.contact_email == request.user.username:
            managed_projects = get_managed_projects(self.request)
            if self.object.project_id not in managed_projects and \
               not views.user_is_allocation_admin(request.user):
                raise PermissionDenied()
        return super(BaseAllocationUpdateView, self) \
            .post(request, *args, **kwargs)


class RestrictedAllocationsEditView(BaseAllocationUpdateView):
    page_title = 'Update'
    template_name = "rcallocation/allocationrequest_user_update.html"
    model = models.AllocationRequest
    form_class = UserAllocationRequestForm
    success_url = "../../"


class RestrictedAllocationsDetailsView(views.AllocationDetailView):
    template_name = "rcallocation/allocationrequest_user_detail.html"
    page_title = 'Details'

    def get(self, request, **kwargs):
        """
        Renders the template with the allocation request and details
        on it.
        """
        self.object = self.get_object()
        # TODO(shauno) Do this somewhere a bit more senisible (model manager?)
        if not self.object.contact_email == request.user.username \
                and not request.user.is_staff:
            managed_projects = get_managed_projects(self.request)
            if self.object.project_id not in managed_projects:
                raise PermissionDenied()
        return super(RestrictedAllocationsDetailsView, self) \
            .get(request, **kwargs)


def get_managed_projects(request):
    try:
        role_assignments = keystone.role_assignments_list(
            request,
            project=request.user.project_id,
            user=request.user.id,
            include_subtree=False,
            include_names=True)
    except:
        role_assignments = []

    for ra in role_assignments:
        if ra.role['name'] == 'TenantManager':
            return [request.user.project_id]

    return []


class UserAllocationsListView(views.AllocationsListView):
    """
    A simple paginated view of the allocation requests, ordered by
    status. Later we should perhaps add sortable columns, filterable
    by status?
    """
    context_object_name = "allocation_list"
    table_class = UserAllocationListTable
    template_name = 'rcallocation/allocationrequest_user_list.html'
    page_title = 'My Requests'

    def get_data(self):
        contact_email = self.request.user.username
        managed_projects = get_managed_projects(self.request)
        return (models.AllocationRequest.objects.all()
                .exclude(status=models.AllocationRequest.LEGACY)
                .filter(parent_request=None)
                .filter(Q(project_id__in=managed_projects) |
                        Q(contact_email__exact=contact_email))
                .order_by('status')
                .prefetch_related('quotas'))
