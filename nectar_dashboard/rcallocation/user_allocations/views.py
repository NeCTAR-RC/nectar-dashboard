import logging
from collections import defaultdict
from functools import partial

from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied

from horizon import tables
from horizon.utils.memoized import memoized
from openstack_dashboard.api import keystone

from nectar_dashboard.rcallocation.models import AllocationRequest, Quota
from nectar_dashboard.rcallocation.views import (AllocationsListView,
                                         AllocationDetailView,
                                         AllocationListTable,
                                         EditRequest)
from nectar_dashboard.rcallocation.views import BaseAllocationView
from nectar_dashboard.rcallocation.forms import QuotaForm

from .forms import UserAllocationRequestForm

LOG = logging.getLogger('nectar_dashboard.rcallocation')


class BaseAllocationUpdateView(BaseAllocationView):
    editor_attr = 'contact_email'
    formset_quota_class = inlineformset_factory(
        AllocationRequest, Quota, form=QuotaForm, extra=0)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_archived():
            raise PermissionDenied()
        if not self.object.contact_email == request.user.username:
            managed_projects = get_managed_projects(self.request)
            if self.object.project_id not in managed_projects:
                raise PermissionDenied()
        return super(BaseAllocationUpdateView, self) \
            .get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_archived():
            raise PermissionDenied()
        if not self.object.contact_email == request.user.username:
            managed_projects = get_managed_projects(self.request)
            if self.object.project_id not in managed_projects:
                raise PermissionDenied()
        return super(BaseAllocationUpdateView, self) \
            .post(request, *args, **kwargs)


class RestrictedAllocationsEditView(BaseAllocationUpdateView):
    template_name = "rcallocation/allocationrequest_user_update.html"
    model = AllocationRequest
    form_class = UserAllocationRequestForm
    success_url = "../../"


class RestrictedAllocationsDetailsView(AllocationDetailView):
    template_name = "rcallocation/allocationrequest_user_detail.html"

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


class UserAmendRequest(tables.LinkAction):
    name = "amend"
    verbose_name = ("Amend/Extend allocation")
    url = "horizon:allocation:user_requests:edit_change_request"
    classes = ("btn-associate",)

    def allowed(self, request, instance):
        return instance.can_be_amended()


class UserEditRequest(EditRequest):
    name = "user_edit"
    verbose_name = ("Edit request")
    url = "horizon:allocation:user_requests:edit_request"

    def allowed(self, request, instance):
        return instance.can_user_edit()


class UserEditChangeRequest(EditRequest):
    name = "user_edit_change"
    verbose_name = ("Edit amend/extend request")
    url = "horizon:allocation:user_requests:edit_change_request"

    def allowed(self, request, instance):
        return instance.can_user_edit_amendment()


class UserAllocationListTable(AllocationListTable):
    view_url = "horizon:allocation:user_requests:allocation_view"

    class Meta(AllocationListTable.Meta):
        row_actions = (UserEditRequest, UserAmendRequest,
                       UserEditChangeRequest)

    def __init__(self, *args, **kwargs):
        super(UserAllocationListTable, self).__init__(*args, **kwargs)
        self.columns['project'].transform = partial(
            self.columns['project'].transform,
            link=self.view_url)


def get_managed_projects(request):
    try:
        role_assignments = keystone.role_assignments_list(
            request,
            project=request.user.project_id,
            user=request.user.id,
            include_names=True)
    except:
        role_assignments = []

    for ra in role_assignments:
        if ra.role['name'] == 'TenantManager':
            return [request.user.project_id]

    return []


class UserAllocationsListView(AllocationsListView):
    """
    A simple paginated view of the allocation requests, ordered by
    status. Later we should perhaps add sortable columns, filterable
    by status?
    """
    context_object_name = "allocation_list"
    table_class = UserAllocationListTable
    template_name = 'rcallocation/allocationrequest_user_list.html'

    def get_data(self):
        contact_email = self.request.user.username
        managed_projects = get_managed_projects(self.request)
        return (AllocationRequest.objects.all()
                .exclude(status='L')
                .filter(parent_request=None)
                .filter(Q(project_id__in=managed_projects) |
                        Q(contact_email__exact=contact_email))
                .order_by('status')
                .prefetch_related('quotas'))
