import logging
from operator import methodcaller

from django.contrib.auth import mixins
from django.db.models import Q
from django.db import transaction
from django.forms.models import inlineformset_factory
from django import http
from django.utils import timezone
from django.views.generic import DetailView
from django.views.generic.edit import ModelFormMixin
from django.views.generic.edit import UpdateView
from horizon import tables as horizon_tables
from horizon import views as horizon_views

from nectar_dashboard.rcallocation import checkers
from nectar_dashboard.rcallocation import forcodes
from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import tables
from nectar_dashboard.rcallocation import utils


LOG = logging.getLogger('nectar_dashboard.rcallocation')


class AllocationDetailView(mixins.UserPassesTestMixin,
                           horizon_views.PageTitleMixin,
                           DetailView, ModelFormMixin):
    """A class that handles rendering the details view, and then the
    posting of the associated accept/reject action
    """

    context_object_name = "allocation"
    model = models.AllocationRequest
    success_url = "../../"
    fields = '__all__'
    page_title = 'View Allocation Request'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        # We need to figure out two things:
        # 1. the latest 'approved' allocation record prior to the one
        #    that we are looking at
        # 2. whether that 'approved' record is the current approval.
        if self.object.is_active():
            approved = self.object
            approved_is_current = not self.object.is_history()
        else:
            parent = (self.object.parent_request or self.object).pk
            all_approved = \
                list(models.AllocationRequest.objects
                     .filter(status=models.AllocationRequest.APPROVED)
                     .filter(parent_request=parent))
            if len(all_approved) == 0:
                approved = None
                approved_is_current = False
            else:
                mod_time = self.object.modified_time
                approved = next(
                    (a for a in all_approved if a.modified_time < mod_time),
                    None)
                approved_is_current = approved == all_approved[0]

        kwargs['approved_allocation'] = approved
        kwargs['approved_is_current'] = approved_is_current
        return super().get_context_data(**kwargs)

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
    page_title = 'Allocation Requests'

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
                'quotas', 'investigators', 'publications', 'grants')

    def test_func(self):
        # Direct uses of this view needs alloc admin access
        return utils.user_is_allocation_admin(self.request.user)


class QuotaFormMixin(object):

    def get_quotas_initial(self):
        initial = {}
        if self.object:
            quotas = self.object.quotas.all_quotas()
            for quota in quotas:
                key = "quota-%s__%s" % (quota.resource.codename,
                                        quota.group.zone.name)
                if self.object.status == models.AllocationRequest.APPROVED:
                    initial[key] = quota.quota
                else:
                    initial[key] = quota.requested_quota
        else:
            for st in models.ServiceType.objects.filter(experimental=False):
                for resource in st.resource_set.filter(requestable=True):
                    for zone in st.zones.all():
                        key = "quota-%s__%s" % (resource.codename, zone.name)
                        initial[key] = resource.default or 0
        return initial

    @staticmethod
    def set_quotas(allocation, form, approving=False):
        non_quota_fields = [f.name for f in allocation._meta.fields
                            + allocation._meta.many_to_many]
        non_quota_fields.append('ignore_warnings')
        for field_name, field in form.fields.items():
            if field_name in non_quota_fields:
                continue
            zone = field.zone
            resource = field.resource
            value = form.cleaned_data[field_name]
            if not allocation.bundle or resource.service_type.is_multizone():
                if value:
                    # Purposely test for 0 or None which means the same thing
                    group, created = models.QuotaGroup.objects.get_or_create(
                        allocation=allocation, zone=zone,
                        service_type=resource.service_type)
                    quota, created = models.Quota.objects.get_or_create(
                        group=group, resource=resource)
                    if approving:
                        quota.quota = value
                    else:
                        quota.requested_quota = value
                    quota.save()
                else:
                    try:
                        group = models.QuotaGroup.objects.get(
                            allocation=allocation, zone=zone,
                            service_type=resource.service_type)
                        quota = models.Quota.objects.get(group=group,
                                                         resource=resource)
                        quota.delete()
                    except (models.QuotaGroup.DoesNotExist,
                            models.Quota.DoesNotExist):
                        pass
            else:
                models.Quota.objects.filter(
                    group__allocation=allocation,
                    resource=resource).delete()
            # Delete empty quota groups
            for group in allocation.quotas.all():
                if group.quota_set.count() < 1:
                    group.delete()


class BaseAllocationView(UpdateView, mixins.UserPassesTestMixin,
                         horizon_views.PageTitleMixin,
                         QuotaFormMixin):

    IGNORE_WARNINGS = False
    APPROVING = False

    model = models.AllocationRequest
    form_class = forms.AllocationRequestForm
    page_title = "Update"

    # investigator
    formset_investigator_class = inlineformset_factory(
        models.AllocationRequest, models.ChiefInvestigator,
        form=forms.ChiefInvestigatorForm,
        extra=0)

    # publication
    formset_publication_class = inlineformset_factory(
        models.AllocationRequest, models.Publication,
        form=forms.PublicationForm, extra=0)

    # grant
    formset_grant_class = inlineformset_factory(
        models.AllocationRequest, models.Grant, form=forms.GrantForm,
        extra=0)

    # The attribute used to record who did the edit.  this should
    # either be approver_email or contact_email
    editor_attr = 'approver_email'

    def get_formset(self, formset_class, queryset=None, prefix=None,
                    initial=None, **kwargs):
        if 'instance' not in kwargs:
            kwargs['instance'] = self.object

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return formset_class(queryset=queryset, prefix=prefix,
                             initial=initial, **kwargs)

    def get_formsets(self):
        formsets = {}
        if self.formset_investigator_class:
            formsets['investigator_formset'] = self.get_formset(
                self.formset_investigator_class)
        if self.formset_publication_class:
            formsets['publication_formset'] = self.get_formset(
                self.formset_publication_class)
        if self.formset_grant_class:
            formsets['grant_formset'] = self.get_formset(
                self.formset_grant_class)
        return formsets

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['for_series'] = forcodes.FOR_SERIES.replace('_', ' ')
        context['bundles'] = models.Bundle.objects.all()
        return context

    def get_initial(self):
        return self.get_quotas_initial()

    def test_func(self):
        # Uses of this view needs alloc admin access ... unless overridden
        return utils.user_is_allocation_admin(self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        approving = self.editor_attr == 'approver_email'

        if self.object:
            # Ensure old projects have to set an investigator
            investigators = self.object.investigators.all()
            if not investigators:
                self.formset_investigator_class = inlineformset_factory(
                    models.AllocationRequest, models.ChiefInvestigator,
                    form=forms.ChiefInvestigatorForm, extra=1)
        else:
            kwargs['object'] = None

        # If this is not already an "edit in progress" make sure
        # that there is at least one Grant in the grant formset to
        # "encourage" the user to either fill it out or click the
        # "I have no grants" button to remove it.
        if self.formset_grant_class \
           and (not self.object
                or self.object.status not in [
                    models.AllocationRequest.SUBMITTED,
                    models.AllocationRequest.UPDATE_PENDING]):
            self.formset_grant_class = inlineformset_factory(
                models.AllocationRequest, models.Grant,
                form=forms.GrantForm,
                min_num=1, extra=0)

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if 'actions' not in kwargs:
            kwargs['actions'] = []  # reduce template debug noise ...
        kwargs['form'] = form
        kwargs.update(self.get_formsets())
        kwargs['warnings'] = []
        kwargs['nags'] = []

        if self.object:
            nag_checker = checkers.NagChecker(
                form=None, allocation=self.object, user=self.request.user)
            nags = nag_checker.do_checks()
            kwargs['nags'] = nags
            if len(nags) > 0:
                tags = [n[0] for n in nags]
                person = 'approver' if approving else 'user'
                LOG.info(f"Showing the {person} nags {tags} "
                         f"for allocation '{self.object.project_name}'")

        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        approving = self.editor_attr == 'approver_email'

        # Create / assemble the form and non-quota formsets.  Note that
        # form instantiation may modify the state of self.object; e.g.
        # the value of self.object.status
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form_dict = self.get_formsets()
        form_dict['form'] = form

        # Check for certain actions / state transitions that will cause
        # major problems if they ever happen.
        if self.object:
            current = models.AllocationRequest.objects.get(id=self.object.id)
            # Any changes to a history record
            if current.parent_request_id:
                return http.HttpResponseBadRequest(
                    'Allocation record is historic')
            if (self.object.status == current.status
                and current.status in (models.AllocationRequest.APPROVED,
                                       models.AllocationRequest.DECLINED,
                                       models.AllocationRequest.UPDATE_DECLINED
                                       )):
                return http.HttpResponseBadRequest(
                    'Allocation state not changing')

        ignore_warnings = self.IGNORE_WARNINGS or \
                          request.POST.get('ignore_warnings', False)

        # Primary validation of quotas + gathering of the values
        # into a format that can be used for quota sanity checks.
        quota_checker = checkers.QuotaSanityChecker(
            allocation=self.object,
            form=form,
            user=self.request.user,
            approving=approving)

        valid = all(map(methodcaller('is_valid'), form_dict.values()))

        if valid:
            warnings = quota_checker.do_checks()
            if len(warnings) == 0:
                return self.form_valid(**form_dict)
            else:
                tags = [w[0] for w in warnings]
                name = form.cleaned_data.get('project_name', '???')
                person = 'approver' if approving else 'user'
                if ignore_warnings:
                    if not self.IGNORE_WARNINGS:
                        LOG.info(f"The {person} ignored warnings {tags} "
                                 f"for allocation '{name}'")
                    return self.form_valid(**form_dict)
                else:
                    form_dict['warnings'] = warnings
                    LOG.info(f"Showing the {person} warnings {tags} "
                             f"for allocation '{name}'")
                    return self.form_invalid(**form_dict)
        else:
            return self.form_invalid(**form_dict)

    @transaction.atomic
    def form_valid(self, form, investigator_formset=None,
                   publication_formset=None, grant_formset=None):
        # Create a new historical object based on the original.
        if self.object:
            utils.copy_allocation(self.object)

        # Save the changes to the request.
        allocation = form.save(commit=False)
        assert self.editor_attr
        if not allocation.created_by:
            allocation.created_by = self.request.user.token.tenant['id']

        # Set the editor attribute
        setattr(allocation, self.editor_attr, self.request.user.username)
        allocation.provisioned = False

        # Force update of submit_date if this a request / amendment
        # submission or resubmission
        if allocation.status in [models.AllocationRequest.NEW,
                             models.AllocationRequest.SUBMITTED,
                             models.AllocationRequest.UPDATE_PENDING]:
            allocation.submit_date = timezone.now()

        # Set the old field to None in the newer allocation request/amend
        allocation.estimated_number_users = None

        allocation.save()
        form.save_m2m()

        formsets = [investigator_formset, publication_formset,
                    grant_formset]

        for formset in formsets:
            if formset:
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.allocation = allocation
                    instance.save()
                for instance in formset.deleted_objects:
                    instance.delete()

        if form.has_quotas:
            self.set_quotas(allocation, form, approving=self.APPROVING)

        # Send notification email
        allocation.send_notifications(extra_context={'request': self.request})
        return http.HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, warnings=[], **formsets):
        """If the form is invalid, re-render the context data with the
        data-filled forms and errors.
        """

        return self.render_to_response(
            self.get_context_data(form=form, warnings=warnings,
                                  form_invalid=True, **formsets))
