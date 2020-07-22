from django.forms.models import inlineformset_factory
from django.urls import reverse

from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import views

from nectar_dashboard.rcallocation.request import forms as request_forms


class UserAllocationRequestForm(forms.AllocationRequestForm):
    class Meta(forms.AllocationRequestForm.Meta):
        exclude = ('project_id', 'status_explanation',
                   ) + forms.AllocationRequestForm.Meta.exclude


class AllocationCreateView(views.BaseAllocationView):
    template_name = "rcallocation/allocationrequest_edit.html"
    form_class = request_forms.UserAllocationRequestForm
    editor_attr = 'contact_email'
    page_title = 'Allocation Request'

    formset_investigator_class = inlineformset_factory(
        models.AllocationRequest, models.ChiefInvestigator,
        form=forms.ChiefInvestigatorForm, extra=1)

    formset_institution_class = inlineformset_factory(
        models.AllocationRequest, models.Institution,
        form=forms.InstitutionForm, extra=1)

    def get_object(self):
        return None

    def get_initial(self):
        return {'contact_email': self.request.user.username}

    def get_success_url(self):
        return reverse('horizon:allocation:user_requests:index')

    def test_func(self):
        return True
