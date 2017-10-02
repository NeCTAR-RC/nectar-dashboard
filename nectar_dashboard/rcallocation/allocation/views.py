from django.forms.models import inlineformset_factory

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation import views
from nectar_dashboard.rcallocation.allocation import forms as allocation_forms


class AllocationUpdateView(views.BaseAllocationView):
    template_name = "rcallocation/allocationrequest_update.html"
    model = models.AllocationRequest
    form_class = forms.AllocationRequestForm
    success_url = "../../"


class AllocationApproveView(views.BaseAllocationView):
    template_name = "rcallocation/allocationrequest_approve.html"
    model = models.AllocationRequest
    form_class = allocation_forms.AllocationApproveForm
    success_url = "../../"
    formset_quota_class = inlineformset_factory(
        models.AllocationRequest, models.Quota,
        form=allocation_forms.QuotaForm, extra=0, can_delete=False)
    formset_investigator_class = inlineformset_factory(
        models.AllocationRequest, models.ChiefInvestigator,
        form=forms.ChiefInvestigatorForm,
        extra=0, can_delete=False)
    formset_institution_class = inlineformset_factory(
        models.AllocationRequest, models.Institution,
        form=forms.InstitutionForm, extra=0,
        can_delete=False)
    formset_publication_class = inlineformset_factory(
        models.AllocationRequest, models.Publication,
        form=forms.PublicationForm, extra=0,
        can_delete=False)
    formset_grant_class = inlineformset_factory(
        models.AllocationRequest, models.Grant,
        form=forms.GrantForm, extra=0, can_delete=False)


class AllocationRejectView(views.BaseAllocationView):
    template_name = "rcallocation/allocationrequest_reject.html"
    model = models.AllocationRequest
    form_class = allocation_forms.AllocationRejectForm
    formset_quota_class = None
    success_url = "../../"
