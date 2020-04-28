from django.contrib.auth import mixins
from django.views.generic.edit import UpdateView

from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import utils
from nectar_dashboard.rcallocation import views

from nectar_dashboard.rcallocation.allocation import forms as allocation_forms
from nectar_dashboard.rcallocation.allocation import tables


class PendingAllocationsListView(views.BaseAllocationsListView):
    table_class = tables.PendingAllocationListTable


class AllocationUpdateView(views.BaseAllocationView):
    allowed_states = [models.AllocationRequest.SUBMITTED,
                      models.AllocationRequest.UPDATE_PENDING]

    template_name = "rcallocation/allocationrequest_update.html"
    model = models.AllocationRequest
    form_class = forms.AllocationRequestForm
    success_url = "../../"
    page_title = 'Update'

class AllocationNotesEdit(mixins.UserPassesTestMixin, UpdateView):
    template_name = "rcallocation/allocationrequest_edit_notes.html"
    model = models.AllocationRequest
    form_class = allocation_forms.EditNotesForm
    page_title = 'Update Notes'

    def test_func(self):
        return utils.user_is_allocation_admin(self.request.user)


class AllocationApproveView(views.BaseAllocationView):
    SHOW_EMPTY_SERVICE_TYPES = False
    ONLY_REQUESTABLE_RESOURCES = False

    page_title = 'Approve'
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


class AllocationRejectView(views.BaseAllocationView):
    IGNORE_WARNINGS = True

    page_title = "Decline"
    template_name = "rcallocation/allocationrequest_reject.html"
    model = models.AllocationRequest
    form_class = allocation_forms.AllocationRejectForm
    quota_form_class = None
    quotagroup_form_class = None
    success_url = "../../"

    formset_investigator_class = None
    formset_institution_class = None
    formset_publication_class = None
    formset_grant_class = None
