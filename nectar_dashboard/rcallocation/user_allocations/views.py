import logging
from collections import defaultdict
from functools import partial

from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied

from horizon import tables
from horizon.utils.memoized import memoized
from openstack_dashboard.api.keystone import keystoneclient

from rcportal.rcallocation.models import AllocationRequest, Quota
from rcportal.rcallocation.views import (AllocationsListView,
                                         AllocationDetailView,
                                         AllocationListTable,
                                         EditRequest)
from rcportal.rcallocation.views import BaseAllocationView
from rcportal.rcallocation.forms import QuotaForm

from .forms import UserAllocationRequestForm

LOG = logging.getLogger('rcportal.rcallocation')


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
            if self.object.tenant_uuid not in managed_projects:
                raise PermissionDenied()
        return super(BaseAllocationUpdateView, self) \
            .get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_archived():
            raise PermissionDenied()
        if not self.object.contact_email == request.user.username:
            managed_projects = get_managed_projects(self.request)
            if self.object.tenant_uuid not in managed_projects:
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
            if self.object.tenant_uuid not in managed_projects:
                raise PermissionDenied()
        return super(RestrictedAllocationsDetailsView, self) \
            .get(request, **kwargs)


class UserAmendRequest(tables.LinkAction):
    name = "amend"
    verbose_name = ("Amend/Extend allocation")
    url = "horizon:project:user_requests:edit_change_request"
    classes = ("btn-associate",)

    def allowed(self, request, instance):
        return instance.can_be_amended()


class UserEditRequest(EditRequest):
    name = "user_edit"
    verbose_name = ("Edit request")
    url = "horizon:project:user_requests:edit_request"

    def allowed(self, request, instance):
        return instance.can_user_edit()


class UserEditChangeRequest(EditRequest):
    name = "user_edit_change"
    verbose_name = ("Edit amend/extend request")
    url = "horizon:project:user_requests:edit_change_request"

    def allowed(self, request, instance):
        return instance.can_user_edit_amendment()


class UserAllocationListTable(AllocationListTable):
    view_url = "horizon:project:user_requests:allocation_view"

    class Meta(AllocationListTable.Meta):
        row_actions = (UserEditRequest, UserAmendRequest,
                       UserEditChangeRequest)

    def __init__(self, *args, **kwargs):
        super(UserAllocationListTable, self).__init__(*args, **kwargs)
        self.columns['project'].transform = partial(
            self.columns['project'].transform,
            link=self.view_url)


@memoized
def get_all_user_roles(request):
    # This is a massive inefficient hack.
    unscoped_token = request.session['unscoped_token']
    client = keystoneclient(request)
    try:
        projects = client.tenants.list()
    except:
        return {}

    roles = defaultdict(set)
    for project in projects:
        try:
            token = client.tokens.authenticate(tenant_id=project.id,
                                               token=unscoped_token)
            project_roles = map(lambda r: r['name'], token.user['roles'])
            roles[project.id] = set(project_roles)
        except:
            pass
    return roles


def get_managed_projects(request):
    projects = get_all_user_roles(request)
    return [project for project, roles in projects.iteritems()
            if 'TenantManager' in roles]


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
                .filter(Q(tenant_uuid__in=managed_projects) |
                        Q(contact_email__exact=contact_email))
                .order_by('status')
                .prefetch_related('quotas'))
