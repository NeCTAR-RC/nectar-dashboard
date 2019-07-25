from collections import OrderedDict
import json
import logging
from operator import methodcaller
import re

from django.contrib.auth import mixins
from django.db.models import Q
from django.db import transaction
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.template import loader
from django.utils import timezone
from django.views.generic import DetailView
from django.views.generic.edit import ModelFormMixin
from django.views.generic.edit import UpdateView
from horizon import tables as horizon_tables
from novaclient import exceptions as n_exc
from openstack_dashboard import api

from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import quota_sanity
from nectar_dashboard.rcallocation import tables
from nectar_dashboard.rcallocation import utils


LOG = logging.getLogger('nectar_dashboard.rcallocation')


class AllocationDetailView(mixins.UserPassesTestMixin, DetailView,
                           ModelFormMixin):
    """A class that handles rendering the details view, and then the
    posting of the associated accept/reject action
    """

    context_object_name = "allocation"
    model = models.AllocationRequest
    success_url = "../../"
    fields = '__all__'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        allocations = (models.AllocationRequest.objects
                       .filter(status=models.AllocationRequest.APPROVED)
                       .filter(parent_request=self.object.pk)[:1])

        if self.object.status == models.AllocationRequest.APPROVED:
            kwargs['previous_allocation'] = self.object
        elif allocations:
            kwargs['previous_allocation'] = allocations[0]
        return (super(AllocationDetailView, self).get_context_data(**kwargs))

    def test_func(self):
        # Direct uses of this view needs alloc admin access
        return utils.user_is_allocation_admin(self.request.user)


class BaseAllocationsListView(mixins.UserPassesTestMixin,
                              horizon_tables.DataTableView):
    """A simple paginated view of the allocation requests, ordered by
    status. Later we should perhaps add sortable columns, filterable
    by status?
    """
    context_object_name = "allocation_list"
    template_name = 'rcallocation/allocationrequest_list.html'
    page_title = 'Requests'

    def get_data(self):
        return [ar for ar in
                models.AllocationRequest.objects.filter(
                    status__in=(models.AllocationRequest.NEW,
                                models.AllocationRequest.SUBMITTED,
                                models.AllocationRequest.UPDATE_PENDING)
                ).filter(
                    parent_request=None).order_by(
                        'submit_date')]

    def test_func(self):
        # Direct uses of this view needs alloc admin access
        return utils.user_is_allocation_admin(self.request.user)


class AllocationHistoryView(mixins.UserPassesTestMixin,
                            horizon_tables.DataTableView):
    """A simple paginated view of the allocation requests, ordered by
    status. Later we should perhaps add sortable columns, filterable
    by status?
    """
    context_object_name = "allocation_list"
    table_class = tables.AllocationHistoryTable
    template_name = 'rcallocation/allocationrequest_list.html'
    page_title = 'History'

    def get_data(self):
        pk = self.kwargs['pk']
        return models.AllocationRequest.objects.filter(
            Q(parent_request=pk) | Q(pk=pk)).prefetch_related(
                'quotas', 'investigators', 'institutions',
                'publications', 'grants')

    def test_func(self):
        # Direct uses of this view needs alloc admin access
        return utils.user_is_allocation_admin(self.request.user)


class BaseAllocationView(mixins.UserPassesTestMixin, UpdateView):
    SHOW_EMPTY_SERVICE_TYPES = True
    ONLY_REQUESTABLE_RESOURCES = True
    IGNORE_WARNINGS = False

    model = models.AllocationRequest
    form_class = forms.AllocationRequestForm
    page_title = "Update"

    quota_form_class = forms.QuotaForm
    quotagroup_form_class = forms.QuotaGroupForm

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
        models.AllocationRequest, models.Grant, form=forms.GrantForm,
        min_num=1, extra=0)

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

    def get_formset(self, formset, queryset=None, prefix=None,
                    initial=None, **kwargs):
        if 'instance' in kwargs:
            instance = kwargs['instance']
        elif 'instance' not in kwargs:
            instance = self.object
        else:
            instance = None
        kwargs = {'instance': instance}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return formset(queryset=queryset, prefix=prefix, initial=initial,
                       **kwargs)

    def get_quota_formsets(self):
        if not self.quotagroup_form_class:
            return []

        resource_kwargs = {}
        quota_kwargs = {}
        if self.ONLY_REQUESTABLE_RESOURCES:
            quota_kwargs['resource__requestable'] = True
            resource_kwargs['requestable'] = True
        else:
            resource_kwargs['requestable'] = False

        quota_formsets = OrderedDict()
        for service_type in models.ServiceType.objects.all():
            existing_groups = []

            initial = []
            existing_resources = []
            if self.object:
                existing_quotas = models.Quota.objects.filter(
                    group__allocation=self.object,
                    resource__service_type=service_type,
                    **quota_kwargs)
                if not existing_quotas and not self.SHOW_EMPTY_SERVICE_TYPES:
                    continue
                if not existing_resources:
                    existing_resources = [quota.resource
                                          for quota in existing_quotas]

            resources = service_type.resource_set.filter(**resource_kwargs)
            for resource in resources:
                if resource not in existing_resources:
                    initial.append({'resource': resource})

            QuotaFormSet = inlineformset_factory(
                models.QuotaGroup, models.Quota,
                form=self.quota_form_class,
                extra=len(initial))

            group_form_args = {'service_type': service_type}
            if self.request.method in ('POST'):
                group_form_args.update({
                    'data': self.request.POST,
                })

            GroupForm = self.quotagroup_form_class
            service_quotas = models.Quota.objects.filter(
                resource__service_type=service_type,
                **quota_kwargs)

            if self.object:
                existing_groups = self.object.quotas.filter(
                    service_type=service_type)
                if existing_groups:
                    qg_formsets = []
                    for quotagroup in existing_groups:
                        form = GroupForm(instance=quotagroup,
                                         prefix="%s_%s" % (
                                             service_type.catalog_name,
                                             quotagroup.id),
                                         **group_form_args)
                        formset = self.get_formset(
                            QuotaFormSet,
                            queryset=service_quotas,
                            prefix="%s_%s" % (service_type.catalog_name,
                                              quotagroup.id),
                            initial=initial,
                            instance=quotagroup,
                        )
                        qg_formsets.append((form, formset))
                    quota_formsets[service_type] = qg_formsets
                else:
                    form = GroupForm(prefix="%s_a" % service_type.catalog_name,
                                     **group_form_args)
                    formset = self.get_formset(
                        QuotaFormSet,
                        queryset=service_quotas,
                        prefix="%s_a" % service_type.catalog_name,
                        initial=initial,
                        instance=None,
                    )
                    quota_formsets[service_type] = [(form, formset)]
            else:
                form = GroupForm(prefix="%s_a" % service_type.catalog_name,
                                 **group_form_args)
                formset = self.get_formset(
                    QuotaFormSet,
                    queryset=service_quotas,
                    prefix="%s_a" % service_type.catalog_name,
                    initial=initial,
                    instance=None,
                )
                quota_formsets[service_type] = [(form, formset)]

            # Find javascript created formsets
            exp = re.compile('%s_(?P<prefix>[b-z])-TOTAL_FORMS' %
                             service_type.catalog_name)
            for key in self.request.POST.keys():
                match = exp.search(key)
                if match:
                    prefix = "%s_%s" % (service_type.catalog_name,
                                        match.group('prefix'))
                    form = GroupForm(prefix=prefix, **group_form_args)
                    formset = self.get_formset(
                        QuotaFormSet,
                        queryset=service_quotas,
                        prefix=prefix,
                        initial=initial,
                        instance=None,
                    )
                    quota_formsets[service_type].append((form, formset))

        return quota_formsets.items()

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
        for zone in models.Zone.objects.filter(enabled=True):
            zones[zone.name] = zone.display_name

        service_types = {}
        for st in models.ServiceType.objects.all():
            service_types[st.catalog_name] = {
                'name': st.name,
                'zones': [{'name': z.name, 'display_name': z.display_name}
                          for z in st.zones.filter(enabled=True)],
            }

        resources = {}
        for resource in models.Resource.objects.all():
            resources[resource.id] = {
                'id': resource.id,
                'name': resource.name,
                'service_type': resource.service_type.catalog_name,
                'quota_name': resource.quota_name,
                'unit': resource.unit,
                'help_text': resource.help_text,
            }

        # Get quota limits for Nova
        quota_limits = {}
        is_invalid = kwargs.get('is_invalid')
        if self.object and self.object.project_id and not is_invalid:
            try:
                quota_limits = api.nova.tenant_absolute_limits(
                    self.request, reserved=True,
                    tenant_id=self.object.project_id)
            except n_exc.Forbidden:
                # required os_compute_api:os-used-limits policy
                pass

        return (super(BaseAllocationView, self)
                .get_context_data(service_types=json.dumps(service_types),
                                  resources=json.dumps(resources),
                                  zones=json.dumps(zones),
                                  quota_limits=json.dumps(quota_limits),
                                  **kwargs))

    def test_func(self):
        # Uses of this view needs alloc admin access ... unless overridden
        return utils.user_is_allocation_admin(self.request.user)

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

        kwargs['form'] = form
        # quota
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
        ignore_warnings = self.IGNORE_WARNINGS or \
                          request.POST.get('ignore_warnings', False)

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

        # Primary validation of quotas + gathering of the values
        # into a form that can be used for quota sanity checks.
        quota_valid = True
        if not ignore_warnings:
            sc_context = quota_sanity.QuotaSanityContext(
                requested=self.ONLY_REQUESTABLE_RESOURCES)

        quota_formsets = self.get_quota_formsets()
        for service_type, form_tuple in quota_formsets:
            selected_zones = []
            for group_form, formset in form_tuple:
                if not formset.is_valid():
                    quota_valid = False
                if not group_form.is_valid():
                    quota_valid = False
                else:
                    if group_form.cleaned_data['zone'] in selected_zones:
                        group_form.add_error(None, "Zones must be unique")
                        quota_valid = False
                    else:
                        selected_zones.append(group_form.cleaned_data['zone'])
                if form.is_valid() and quota_valid and not ignore_warnings:
                    quotas_to_check = self._prep_quotas(form, group_form,
                                                        formset)
                    sc_context.add_quotas(quotas_to_check)

        valid = quota_valid and \
            all(map(methodcaller('is_valid'), kwargs.values()))
        kwargs['quota_formsets'] = quota_formsets

        if valid:
            if ignore_warnings:
                return self.form_valid(**kwargs)
            warnings = sc_context.do_checks()
            if len(warnings) == 0:
                return self.form_valid(**kwargs)
            else:
                kwargs['warnings'] = warnings
                return self.form_invalid(**kwargs)
        else:
            return self.form_invalid(**kwargs)

    def _prep_quotas(self, form, group_form, formset):
        # Connect up the quotas, groups and allocation so that the
        # quotas can be properly identified by the sanity checker.
        object = form.save(commit=False)
        group = group_form.save(commit=False)
        group.allocation = object
        zone = group_form.cleaned_data.get('zone', None)
        if zone is None:
            zone_name = 'nectar'
        else:
            zone_name = zone.name
        try:
            group.zone = models.Zone.objects.filter(name=zone_name)[0]
        except IndexError:
            raise Exception("Unknown zone %s" % zone_name)

        quotas_to_check = []
        for quota_data in formset.cleaned_data:
            q = quota_data.get('id', None)
            if q is None:
                q = models.Quota()
                q.resource = quota_data['resource']
            q.quota = quota_data.get('quota', 0)
            q.requested_quota = quota_data.get('requested_quota', 0)
            q.group = group
            quotas_to_check.append(q)
        return quotas_to_check

    @transaction.atomic
    def form_valid(self, form, investigator_formset=None,
                   institution_formset=None, publication_formset=None,
                   grant_formset=None, quota_formsets=[]):
        # Create a new historical object based on the original.
        if self.object:
            utils.copy_allocation(self.object)

        # Save the changes to the request.
        object = form.save(commit=False)
        assert self.editor_attr
        if not object.created_by:
            object.created_by = self.request.user.token.tenant['id']

        # Set the editor attribute
        setattr(object, self.editor_attr, self.request.user.username)
        object.provisioned = False

        # Force update of submit_date if this a request / ammendment
        # submission or resubmission
        if object.status in [models.AllocationRequest.NEW,
                             models.AllocationRequest.SUBMITTED,
                             models.AllocationRequest.UPDATE_PENDING]:
            object.submit_date = timezone.now()

        object.save()
        self.object = object

        # quota formsets handled slightly differently as we want to
        # drop objects if requested_quota == 0
        # Default quotas are zero so requesting 0 is not needed
        for service_type, form_tuple in quota_formsets:
            for group_form, quota_formset in form_tuple:
                quotas_to_save = []

                quotas = quota_formset.save(commit=False)
                for obj in quota_formset.deleted_objects:
                    obj.delete()

                # If quota is set to zero then delete the resource
                # If unavailable qotas are visible then its approval
                # And we want to determin by quota as opposed to requested
                for quota in quotas:
                    if self.ONLY_REQUESTABLE_RESOURCES:
                        zero_check = quota.requested_quota
                    else:
                        zero_check = quota.quota

                    if zero_check > 0:
                        quotas_to_save.append(quota)
                    else:
                        if quota.id:
                            quota.delete()

                if quotas_to_save or group_form.instance.id:
                    group = group_form.save(commit=False)
                    group.allocation = self.object
                    group.save()
                    for quota in quotas_to_save:
                        quota.group = group
                        quota.save()

        # Delete empty quota groups
        for group in self.object.quotas.all():
            if group.quota_set.count() < 1:
                group.delete()

        formsets = [investigator_formset, institution_formset,
                    publication_formset, grant_formset]

        for formset in formsets:
            if formset:
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.allocation = self.object
                    instance.save()
                for instance in formset.deleted_objects:
                    instance.delete()

        # Send notification email
        self.object.send_notifications(extra_context={'request': self.request})

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, investigator_formset=None,
                     institution_formset=None, publication_formset=None,
                     grant_formset=None, quota_formsets=None,
                     warnings=[]):
        """If the form is invalid, re-render the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  investigator_formset=investigator_formset,
                                  institution_formset=institution_formset,
                                  publication_formset=publication_formset,
                                  grant_formset=grant_formset,
                                  quota_formsets=quota_formsets,
                                  is_invalid=True, warnings=warnings))
