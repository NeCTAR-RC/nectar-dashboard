import logging

from nectar_dashboard.rcallocation.allocation_approved import tables
from nectar_dashboard.rcallocation.allocation import forms as allocation_forms
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import views


LOG = logging.getLogger('nectar_dashboard.rcallocation')


class ApprovedAllocationsListView(views.BaseAllocationsListView):
    page_title = 'Approved Requests'
    table_class = tables.ApprovedAllocationListTable

    def get_data(self):
        return [ar for ar in
                models.AllocationRequest.objects.filter(
                    parent_request=None).filter(
                    status__in=('A', 'X', 'J')).order_by(
                    'project_name')]


class AllocationUpdateView(views.BaseAllocationView):
    allowed_states = [models.AllocationRequest.APPROVED,]
    ONLY_REQUESTABLE_RESOURCES = False
    SHOW_EMPTY_SERVICE_TYPES = False

    page_title = 'Update'
    template_name = "rcallocation/allocationrequest_approve.html"
    model = models.AllocationRequest
    form_class = allocation_forms.AllocationApproveForm
    quota_form_class = allocation_forms.QuotaForm
    quotagroup_form_class = allocation_forms.QuotaGroupForm
    success_url = "../../"

    formset_investigator_class = None
    formset_institution_class = None
    formset_publication_class = None
    formset_grant_class = None
