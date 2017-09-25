from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.db import transaction

from nectar_dashboard.rcallocation.forms import AllocationRequestForm, \
    QuotaForm, QuotaInlineFormSet, ChiefInvestigatorForm, InstitutionForm, \
    PublicationForm, GrantForm
from nectar_dashboard.rcallocation.views import BaseAllocationView
from nectar_dashboard.rcallocation.models import AllocationRequest, Quota, \
    ChiefInvestigator, Institution, Publication, Grant


class UserAllocationRequestForm(AllocationRequestForm):
    class Meta(AllocationRequestForm.Meta):
        exclude = ('tenant_uuid', 'status_explanation',
                   'instance_quota', 'core_quota', 'ram_quota',
                   ) + AllocationRequestForm.Meta.exclude


class AllocationCreateView(BaseAllocationView):
    template_name = "rcallocation/allocationrequest_edit.html"
    form_class = UserAllocationRequestForm
    editor_attr = 'contact_email'
    formset_quota_class = inlineformset_factory(
        AllocationRequest, Quota, form=QuotaForm,
        formset=QuotaInlineFormSet, extra=0)

    formset_investigator_class = inlineformset_factory(
        AllocationRequest, ChiefInvestigator, form=ChiefInvestigatorForm,
        extra=1)

    formset_institution_class = inlineformset_factory(
        AllocationRequest, Institution, form=InstitutionForm, extra=1)

    formset_publication_class = inlineformset_factory(
        AllocationRequest, Publication, form=PublicationForm, extra=0)

    formset_grant_class = inlineformset_factory(
        AllocationRequest, Grant, form=GrantForm, extra=0)

    def get_object(self):
        return None

    def get_initial(self):
        return {'contact_email': self.request.user.username}

    def get_success_url(self):
        return reverse('horizon:allocation:user_requests:index')

    @transaction.atomic
    def form_valid(self, form, quotaFormSet=None, investigatorFormSet=None,
                   institutionFormSet=None, publicationFormSet=None,
                   grantFormSet=None):
        # Save the changes to the request.
        object = form.save(commit=False)
        assert self.editor_attr
        object.created_by = self.request.user.token.tenant['id']
        # Set the editor attribute
        setattr(object, self.editor_attr, self.request.user.username)
        object.save()

        # This is a create operation so we need regenerate the formset
        # with an object to set the foreign key as.  This is a side
        # effect of the get_formset method and requires self.object to
        # be set.
        self.object = object
        formset_quota_class = self.get_formset_quota_class()
        quotaFormSet = self.get_formset(formset_quota_class)
        quotaFormSet.is_valid()
        quotaFormSet.save()

        # chief investigator
        formset_investigator_class = self.get_formset_investigator_class()
        investigatorFormSet = self.get_formset(formset_investigator_class)
        investigatorFormSet.is_valid()
        investigatorFormSet.save()

        # institutions
        formset_institution_class = self.get_formset_institution_class()
        institutionFormSet = self.get_formset(formset_institution_class)
        institutionFormSet.is_valid()
        institutionFormSet.save()

        # publications
        formset_publication_class = self.get_formset_publication_class()
        publicationFormSet = self.get_formset(formset_publication_class)
        publicationFormSet.is_valid()
        publicationFormSet.save()

        # grant
        formset_grant_class = self.get_formset_grant_class()
        grantFormSet = self.get_formset(formset_grant_class)
        grantFormSet.is_valid()
        grantFormSet.save()

        return HttpResponseRedirect(self.get_success_url())
