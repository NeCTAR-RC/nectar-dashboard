from django.views.generic.edit import UpdateView
from django.core.exceptions import PermissionDenied

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation import utils
from nectar_dashboard.rcallocation import views

from nectar_dashboard.rcallocation.allocation import forms as allocation_forms


class AllocationUpdateView(views.BaseAllocationView):
    template_name = "rcallocation/allocationrequest_update.html"
    model = models.AllocationRequest
    form_class = forms.AllocationRequestForm
    success_url = "../../"
    page_title = 'Update'


class AllocationNotesEdit(UpdateView):
    template_name = "rcallocation/allocationrequest_edit_notes.html"
    model = models.AllocationRequest
    form_class = allocation_forms.EditNotesForm
    page_title = 'Update Notes'

    def get(self, request, *args, **kwargs):
        if not utils.user_is_allocation_admin(request.user):
            raise PermissionDenied()
        return super(AllocationNotesEdit, self).get(request, **kwargs)

    def post(self, request, *args, **kwargs):
        if not utils.user_is_allocation_admin(request.user):
            raise PermissionDenied()
        return super(AllocationNotesEdit, self).post(request, **kwargs)


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
