import logging
import json
from operator import methodcaller

from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import ModelFormMixin
from django.forms.models import inlineformset_factory
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template import loader
from django.conf import settings
from horizon import tables as horizon_tables

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation import tables


LOG = logging.getLogger('nectar_dashboard.rcallocation')


class AllocationDetailView(DetailView, ModelFormMixin):
    """
    A class that handles rendering the details view, and then the
    posting of the associated accept/reject action
    """

    context_object_name = "allocation"
    model = models.AllocationRequest
    success_url = "../../"

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        allocations = (models.AllocationRequest.objects
                       .filter(status=models.AllocationRequest.APPROVED)
                       .filter(parent_request=self.object.pk)
                       .order_by('-modified_time')[:1])

        if allocations:
            kwargs['previous_allocation'] = allocations[0]
        elif self.object.status == models.AllocationRequest.APPROVED:
            kwargs['previous_allocation'] = self.object
        return (super(AllocationDetailView, self).get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        pass


class AllocationsListView(horizon_tables.DataTableView):
    """
    A simple paginated view of the allocation requests, ordered by
    status. Later we should perhaps add sortable columns, filterable
    by status?
    """
    context_object_name = "allocation_list"
    table_class = tables.AllocationListTable
    template_name = 'rcallocation/allocationrequest_list.html'

    def get_data(self):
        return [ar for ar in
                models.AllocationRequest.objects.filter(
                    status__in=(models.AllocationRequest.NEW,
                                models.AllocationRequest.SUBMITTED,
                                models.AllocationRequest.UPDATE_PENDING)
                ).filter(
                    parent_request=None).order_by(
                        'modified_time').prefetch_related(
                            'quotas', 'investigators', 'institutions',
                            'publications', 'grants')]


class AllocationHistoryView(horizon_tables.DataTableView):
    """
    A simple paginated view of the allocation requests, ordered by
    status. Later we should perhaps add sortable columns, filterable
    by status?
    """
    context_object_name = "allocation_list"
    table_class = tables.AllocationHistoryTable
    template_name = 'rcallocation/allocationrequest_list.html'

    def get_data(self):
        pk = self.kwargs['pk']
        return models.AllocationRequest.objects.filter(
            Q(parent_request=pk) | Q(pk=pk)).order_by(
                '-modified_time').prefetch_related(
                    'quotas', 'investigators', 'institutions',
                    'publications', 'grants')


def copy_allocation(allocation):
    old_object = models.AllocationRequest.objects.get(id=allocation.id)
    old_object.parent_request = allocation
    quotas = old_object.quotas.all()
    investigators = old_object.investigators.all()
    institutions = old_object.institutions.all()
    publications = old_object.publications.all()
    grants = old_object.grants.all()

    old_object.id = None
    old_object.save()

    for quota in quotas:
        quota.id = None
        quota.allocation = old_object
        quota.save()

    for inv in investigators:
        inv.id = None
        inv.allocation = old_object
        inv.save()

    for inst in institutions:
        inst.id = None
        inst.allocation = old_object
        inst.save()

    for pub in publications:
        pub.id = None
        pub.allocation = old_object
        pub.save()

    for grant in grants:
        grant.id = None
        grant.allocation = old_object
        grant.save()


class BaseAllocationView(UpdateView):
    SHOW_EMPTY_SERVICE_TYPES = True

    model = models.AllocationRequest
    form_class = forms.AllocationRequestForm
    page_title = "Update"

    quota_form_class = forms.QuotaForm
    # investigator
    formset_investigator_class = inlineformset_factory(
        models.AllocationRequest, models.ChiefInvestigator,
        form=forms.ChiefInvestigatorForm,
        extra=0)

    # institution
    formset_institution_class = inlineformset_factory(
        models.AllocationRequest, models.Institution,
        form=forms.InstitutionForm, extra=0)

    # publication
    formset_publication_class = inlineformset_factory(
        models.AllocationRequest, models.Publication,
        form=forms.PublicationForm, extra=0)

    # grant
    formset_grant_class = inlineformset_factory(
        models.AllocationRequest, models.Grant, form=forms.GrantForm, extra=0)

    # The attribute used to record who did the edit.  this should
    # either be approver_email or contact_email
    editor_attr = 'approver_email'

    def __init__(self, **kwargs):
        super(BaseAllocationView, self).__init__(**kwargs)

        # investigator
        FormSet_Investigator_Class = self.get_formset_investigator_class()
        if FormSet_Investigator_Class:
            self.formset_investigator_tmpl = loader.render_to_string(
                'rcallocation/investigator_form.html',
                {'investigator_form': FormSet_Investigator_Class().empty_form})
        else:
            self.formset_investigator_tmpl = ""

        # institution
        FormSet_Institution_Class = self.get_formset_institution_class()
        if FormSet_Institution_Class:
            self.formset_institution_tmpl = loader.render_to_string(
                'rcallocation/institution_form.html',
                {"institution_form": FormSet_Institution_Class().empty_form})
        else:
            self.formset_institution_tmpl = ""

        # publication
        FormSet_Publication_Class = self.get_formset_publication_class()
        if FormSet_Publication_Class:
            self.formset_publication_tmpl = loader.render_to_string(
                'rcallocation/publication_form.html',
                {"publication_form": FormSet_Publication_Class().empty_form})
        else:
            self.formset_publication_tmpl = ""

        # grant
        FormSet_Grant_Class = self.get_formset_grant_class()
        if FormSet_Grant_Class:
            self.formset_grant_tmpl = loader.render_to_string(
                'rcallocation/grant_form.html',
                {"grant_form": FormSet_Grant_Class().empty_form})
        else:
            self.formset_grant_tmpl = ""

    def get_formset_investigator_class(self):
        return self.formset_investigator_class

    def get_formset_institution_class(self):
        return self.formset_institution_class

    def get_formset_publication_class(self):
        return self.formset_publication_class

    def get_formset_grant_class(self):
        return self.formset_grant_class

    def get_formset(self, formset, queryset=None, prefix=None, initial=None):
        kwargs = {'instance': self.object}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return formset(queryset=queryset, prefix=prefix, initial=initial,
                       **kwargs)

    def get_quota_formsets(self):
        quota_formsets = []
        for service_type in models.ServiceType.objects.all():
            initial = []
            existing_resources = []
            if self.object:
                existing_quotas = self.object.quotas.filter(
                    resource__service_type=service_type)
                if not existing_quotas and not self.SHOW_EMPTY_SERVICE_TYPES:
                    continue
                if not existing_resources:
                    existing_resources = [quota.resource
                                          for quota in existing_quotas]

            for resource in service_type.resource_set.all():
                if resource not in existing_resources:
                    initial.append({'resource': resource})

            QuotaFormSet = inlineformset_factory(
                models.AllocationRequest, models.Quota,
                form=self.quota_form_class, formset=forms.QuotaInlineFormSet,
                extra=len(initial))

            formset = self.get_formset(
                QuotaFormSet,
                queryset=models.Quota.objects.filter(
                    resource__service_type=service_type),
                prefix=service_type.catalog_name,
                initial=initial
            )
            quota_formsets.append((service_type, formset))
        return quota_formsets

    def get_context_data(self, **kwargs):
        # investigator
        if self.formset_investigator_tmpl:
            kwargs['investigatorFormTmpl'] = self.formset_investigator_tmpl

        # institution
        if self.formset_institution_tmpl:
            kwargs['institutionFormTmpl'] = self.formset_institution_tmpl

        # publication
        if self.formset_publication_tmpl:
            kwargs['publicationFormTmpl'] = self.formset_publication_tmpl

        # grant
        if self.formset_grant_tmpl:
            kwargs['grantFormTmpl'] = self.formset_grant_tmpl

        zones = {}
        for zone in models.Zone.objects.all():
            zones[zone.name] = zone.display_name

        service_types = {}
        for st in models.ServiceType.objects.all():
            service_types[st.catalog_name] = {
                'name': st.name,
                'zones': [{'name': z.name, 'display_name': z.display_name}
                          for z in st.zones.all()],
            }

        resources = {}
        for resource in models.Resource.objects.all():
            resources[resource.id] = {
                'id': resource.id,
                'name': resource.name,
                'service_type': resource.service_type.catalog_name,
                'quota_name': resource.quota_name,
                'unit': resource.unit,
            }

        return (super(BaseAllocationView, self)
                .get_context_data(service_types=json.dumps(service_types),
                                  resources=json.dumps(resources),
                                  zones=json.dumps(zones),
                                  **kwargs))


    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object:

            # Ensure old projects have to set an investigator and
            # an institution
            investigators = self.object.investigators.all()
            if not investigators:
                self.formset_investigator_class = inlineformset_factory(
                    models.AllocationRequest, models.ChiefInvestigator,
                    form=forms.ChiefInvestigatorForm, extra=1)

            institutions = self.object.institutions.all()

            if not institutions:
                self.formset_institution_class = inlineformset_factory(
                    models.AllocationRequest, models.Institution,
                    form=forms.InstitutionForm,
                    extra=1)

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        kwargs = {'form': form}
        # quota
        if self.quota_form_class:
            kwargs['quota_formsets'] = self.get_quota_formsets()

        # investigator
        formset_investigator_class = self.get_formset_investigator_class()
        if formset_investigator_class:
            kwargs['investigator_formset'] = self.get_formset(
                formset_investigator_class)

        # institution
        formset_institution_class = self.get_formset_institution_class()
        if formset_institution_class:
            kwargs['institution_formset'] = self.get_formset(
                formset_institution_class)

        # publication
        formset_publication_class = self.get_formset_publication_class()
        if formset_publication_class:
            kwargs['publication_formset'] = self.get_formset(
                formset_publication_class)

        # grant
        formset_grant_class = self.get_formset_grant_class()
        if formset_grant_class:
            kwargs['grant_formset'] = self.get_formset(formset_grant_class)

        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        kwargs = {'form': form}

        formset_investigator_class = self.get_formset_investigator_class()
        if formset_investigator_class:
            kwargs['investigator_formset'] = self.get_formset(
                formset_investigator_class)

        formset_institution_class = self.get_formset_institution_class()
        if formset_institution_class:
            kwargs['institution_formset'] = self.get_formset(
                formset_institution_class)
        formset_publication_class = self.get_formset_publication_class()
        if formset_publication_class:
            kwargs['publication_formset'] = self.get_formset(
                formset_publication_class)

        formset_grant_class = self.get_formset_grant_class()
        if formset_grant_class:
            kwargs['grant_formset'] = self.get_formset(formset_grant_class)

        quota_valid = True
        quota_formsets = None
        if self.quota_form_class:
            quota_formsets = self.get_quota_formsets()
            for service_type, formset in quota_formsets:
                if not formset.is_valid():
                    quota_valid = False

        if quota_valid and all(map(methodcaller('is_valid'), kwargs.values())):
            return self.form_valid(quota_formsets=quota_formsets, **kwargs)
        else:
            return self.form_invalid(quota_formsets=quota_formsets, **kwargs)

    @transaction.atomic
    def form_valid(self, form, investigator_formset=None,
                   institution_formset=None, publication_formset=None,
                   grant_formset=None, quota_formsets=None):
        # Create a new historical object based on the original.
        if self.object:
            copy_allocation(self.object)

        # Save the changes to the request.
        object = form.save(commit=False)
        assert self.editor_attr
        if not object.created_by:
            object.created_by = self.request.user.token.tenant['id']

        # Set the editor attribute
        setattr(object, self.editor_attr, self.request.user.username)
        object.provisioned = False
        object.save()
        self.object = object

        # quota formsets handled slightly differently as we want to
        # drop objects if requested_quota == 0
        # Default quotas are zero so requesting 0 is not needed
        if quota_formsets:
            for service_type, quota_formset in quota_formsets:
                quotas = quota_formset.save(commit=False)
                for obj in quota_formset.deleted_objects:
                    obj.delete()
                for quota in quotas:
                    if quota.requested_quota > 0:
                        quota.allocation = self.object
                        quota.save()
                    else:
                        if quota.id:
                            quota.delete()

        formsets = [investigator_formset, institution_formset,
                    publication_formset, grant_formset]

        for formset in formsets:
            if formset:
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.allocation = self.object
                    instance.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, investigator_formset=None,
                     institution_formset=None, publication_formset=None,
                     grant_formset=None, quota_formsets=None):
        """
        If the form is invalid, re-render the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  investigator_formset=investigator_formset,
                                  institution_formset=institution_formset,
                                  publication_formset=publication_formset,
                                  grant_formset=grant_formset,
                                  quota_formsets=quota_formsets))
