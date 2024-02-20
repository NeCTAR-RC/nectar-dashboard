from django.contrib.auth import mixins
from django import http
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
    template_name = "rcallocation/allocationrequest_update.html"
    model = models.AllocationRequest
    form_class = forms.AllocationRequestForm
    success_url = "../../"
    page_title = 'Update'


class AllocationNotesEdit(mixins.UserPassesTestMixin, UpdateView):
    template_name = "rcallocation/allocationrequest_edit_notes.html"
    model = models.AllocationRequest
    form_class = allocation_forms.EditNotesForm
    page_title = 'Edit Allocation Admin Notes'

    def test_func(self):
        return utils.user_is_allocation_admin(self.request.user)

    def form_valid(self, form, investigator_formset=None,
                   publication_formset=None, grant_formset=None):

        # Save the changes to the request.
        allocation = form.save(commit=False)
        allocation.save_without_updating_timestamps()
        return http.HttpResponseRedirect(self.get_success_url())


class AllocationApproveView(views.BaseAllocationView):

    APPROVING = True

    page_title = 'Approve Request'
    template_name = "rcallocation/allocationrequest_approve.html"
    model = models.AllocationRequest
    form_class = allocation_forms.AllocationApproveForm
    success_url = "../../"

    formset_investigator_class = None
    formset_institution_class = None
    formset_publication_class = None
    formset_grant_class = None

    def get(self, request, *args, **kwargs):
        allocation = self.get_object()
        if allocation.is_active():
            return http.HttpResponseBadRequest(
                'Allocation already approved')
        return super().get(request, *args, **kwargs)


class AllocationRejectView(views.BaseAllocationView):
    IGNORE_WARNINGS = True

    page_title = "Decline or Request Changes from User"
    template_name = "rcallocation/allocationrequest_reject.html"
    model = models.AllocationRequest
    form_class = allocation_forms.AllocationRejectForm
    success_url = "../../"

    formset_investigator_class = None
    formset_institution_class = None
    formset_publication_class = None
    formset_grant_class = None

    def get(self, request, *args, **kwargs):
        allocation = self.get_object()
        if allocation.is_rejected():
            return http.HttpResponseBadRequest(
                'Allocation already declined')
        return super().get(request, *args, **kwargs)
