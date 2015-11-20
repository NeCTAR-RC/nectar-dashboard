from django.forms.models import inlineformset_factory

from nectar_dashboard.rcallocation.models import AllocationRequest, Quota, \
    ChiefInvestigator, Institution, Publication, Grant
from nectar_dashboard.rcallocation.forms import AllocationRequestForm, \
    ChiefInvestigatorForm, InstitutionForm, PublicationForm, GrantForm
from nectar_dashboard.rcallocation.views import BaseAllocationView
from .forms import (
    AllocationApproveForm,
    AllocationRejectForm,
    AllocationProvisionForm,
    QuotaForm,
)


class AllocationUpdateView(BaseAllocationView):
    template_name = "rcallocation/allocationrequest_update.html"
    model = AllocationRequest
    form_class = AllocationRequestForm
    success_url = "../../"


class AllocationApproveView(BaseAllocationView):
    template_name = "rcallocation/allocationrequest_approve.html"
    model = AllocationRequest
    form_class = AllocationApproveForm
    success_url = "../../"
    formset_quota_class = inlineformset_factory(
        AllocationRequest, Quota, form=QuotaForm, extra=0, can_delete=False)
    formset_investigator_class = inlineformset_factory(
        AllocationRequest, ChiefInvestigator, form=ChiefInvestigatorForm,
        extra=0, can_delete=False)
    formset_institution_class = inlineformset_factory(
        AllocationRequest, Institution, form=InstitutionForm, extra=0,
        can_delete=False)
    formset_publication_class = inlineformset_factory(
        AllocationRequest, Publication, form=PublicationForm, extra=0,
        can_delete=False)
    formset_grant_class = inlineformset_factory(
        AllocationRequest, Grant, form=GrantForm, extra=0, can_delete=False)


class AllocationRejectView(BaseAllocationView):
    template_name = "rcallocation/allocationrequest_reject.html"
    model = AllocationRequest
    form_class = AllocationRejectForm
    formset_quota_class = None
    success_url = "../../"


class AllocationProvisionView(BaseAllocationView):
    template_name = "rcallocation/allocationrequest_provision.html"
    model = AllocationRequest
    form_class = AllocationProvisionForm
    formset_quota_class = None
    success_url = "../../"
