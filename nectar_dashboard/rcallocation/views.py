import logging
import json
from operator import methodcaller

from django.views.generic.edit import UpdateView
from django.forms.models import inlineformset_factory
from django.db import transaction
from django.http import HttpResponseRedirect
from django.core import urlresolvers
from django.db.models import Q
from django.template import loader
from django.views.generic import DetailView
from django.views.generic.edit import ModelFormMixin
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.html import escape
from horizon import tables

from nectar_dashboard.rcallocation.forms import AllocationRequestForm
from nectar_dashboard.rcallocation.models import AllocationRequest, \
    ChiefInvestigator, Quota, Institution, Publication, Grant
from forms import QuotaForm, ChiefInvestigatorForm, InstitutionForm, \
    PublicationForm, GrantForm

LOG = logging.getLogger('nectar_dashboard.rcallocation')


def user_is_allocation_admin(user):
    return user.has_perm('openstack.roles.allocationadmin')


class AllocationDetailView(DetailView, ModelFormMixin):
    """
    A class that handles rendering the details view, and then the
    posting of the associated accept/reject action
    """

    context_object_name = "allocation"
    model = AllocationRequest
    success_url = "../../"

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        allocations = (AllocationRequest.objects
                       .filter(status='A')
                       .filter(parent_request=self.object.pk)
                       .order_by('-modified_time')[:1])

        if allocations:
            kwargs['previous_allocation'] = allocations[0]
        elif self.object.status == 'A':
            kwargs['previous_allocation'] = self.object
        return (super(AllocationDetailView, self).get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        pass


# Actions
class EditRequest(tables.LinkAction):
    name = "edit"
    verbose_name = ("Edit request")
    url = "horizon:allocation:requests:edit_request"
    classes = ("btn-associate",)

    def allowed(self, request, instance):
        return instance.can_be_edited() or (
            instance.can_admin_edit() and
            user_is_allocation_admin(request.user))


class ApproveRequest(tables.LinkAction):
    name = "approve"
    verbose_name = ("Approve request")
    url = "horizon:allocation:requests:approve_request"
    classes = ("btn-associate",)

    def allowed(self, request, instance):
        return instance.can_be_approved()


class RejectRequest(tables.LinkAction):
    name = "reject"
    verbose_name = ("Request changes from user")
    url = "horizon:allocation:requests:reject_request"
    classes = ("btn-associate",)

    def allowed(self, request, instance):
        return instance.can_be_rejected() or instance.can_reject_change()


class ApproveChangeRequest(tables.LinkAction):
    name = "approve_change"
    verbose_name = ("Approve change request")
    url = "horizon:allocation:requests:approve_change_request"
    classes = ("btn-associate",)

    def allowed(self, request, instance):
        return instance.can_approve_change()


class ViewHistory(tables.LinkAction):
    name = "view_history"
    verbose_name = "View history"
    url = "horizon:allocation:requests:allocation_history"


def status_icon(allocation):
    css_style = 'alloc-icon-wip'
    title = allocation.get_status_display()
    text = allocation.status
    if allocation.status == 'A':
        css_style = 'alloc-icon-ok'
    data = mark_safe('<p'
                     ' title="%s"'
                     ' class="alloc-icon %s">'
                     '<strong>%s</strong></p>'
                     % (title, css_style, text))
    return data


def allocation_title(allocation,
                     link='horizon:allocation:requests:allocation_view'):
    url = urlresolvers.reverse(link, args=(allocation.pk,))
    # Escape the data inside while allowing our HTML to render
    data = mark_safe('<a href="%s">%s</a>'
                     '<br/>'
                     '<small class="muted">%s</small>' %
                     (escape(url),
                      escape(unicode(allocation.project_name)),
                      escape(unicode(allocation.tenant_name))))
    return data


class AllocationListTable(tables.DataTable):
    status = tables.Column(status_icon,
                           classes=['text-center'],
                           verbose_name="State")
    project = tables.Column(allocation_title,
                            verbose_name="Research Description", )
    allocation_home = tables.Column('allocation_home',
                                    verbose_name='Allocation Home Location')
    contact = tables.Column("contact_email", verbose_name="Contact")
    modified_time = tables.Column("modified_time",
                                  verbose_name="Last Updated",
                                  filters=[lambda d: d.date()])
    end_date = tables.Column("end_date",
                             verbose_name="Expiry Date")

    class Meta:
        verbose_name = "Requests"
        row_actions = (EditRequest, ViewHistory,)


def delta_quota(allocation, want, have):
    if allocation.status in ('X', 'J'):
        return "%+d" % (int(want) - int(have))
    elif allocation.status == 'A':
        return have or '-'
    elif allocation.status in ('E', 'R'):
        return want or '-'
    return "Requested %s, currently have %s" % (want, have)


def get_quota(wanted, actual=None):
    def quota(allocation):
        want = getattr(allocation, wanted)
        have = getattr(allocation, actual, want)
        return delta_quota(allocation, want, have)
    return quota


def get_quota_by_resource(resource):
    def quota(allocation):
        want = 0
        have = 0
        for quota in allocation.quotas.all():
            if quota.resource != resource:
                continue
            want += quota.requested_quota
            have += quota.quota
        return delta_quota(allocation, want, have)
    return quota


class AllocationHistoryTable(tables.DataTable):
    project = tables.Column("project_name", verbose_name="Project name",
                            link="horizon:allocation:requests:allocation_view")
    approver = tables.Column("approver_email", verbose_name="Approver")
    instances = tables.Column(
        get_quota("instances", "instance_quota"),
        verbose_name="Instances")
    cores = tables.Column(
        get_quota("cores", "core_quota"),
        verbose_name="Cores")
    object_store = tables.Column(
        get_quota_by_resource("object"),
        verbose_name="Object Storage")
    volume_storage = tables.Column(
        get_quota_by_resource("volume"),
        verbose_name="Volume Storage")
    status = tables.Column("get_status_display", verbose_name="Status")
    modified_time = tables.Column(
        "modified_time", verbose_name="Modification time")

    class Meta:
        verbose_name = "Request History"


class AllocationsListView(tables.DataTableView):
    """
    A simple paginated view of the allocation requests, ordered by
    status. Later we should perhaps add sortable columns, filterable
    by status?
    """
    context_object_name = "allocation_list"
    table_class = AllocationListTable
    template_name = 'rcallocation/allocationrequest_list.html'
    page_title = 'Requests'

    def get_data(self):
        return [ar for ar in
                AllocationRequest.objects.filter(
                    status__in=('N', 'E', 'X')).filter(
                    parent_request=None).order_by(
                    'modified_time').prefetch_related(
                    'quotas', 'investigators', 'institutions',
                    'publications', 'grants')]


class AllocationHistoryView(tables.DataTableView):
    """
    A simple paginated view of the allocation requests, ordered by
    status. Later we should perhaps add sortable columns, filterable
    by status?
    """
    context_object_name = "allocation_list"
    table_class = AllocationHistoryTable
    template_name = 'rcallocation/allocationrequest_list.html'
    page_title = 'History'

    def get_data(self):
        pk = self.kwargs['pk']
        return [ar for ar in
                AllocationRequest.objects.filter(
                    Q(parent_request=pk) | Q(pk=pk)).order_by(
                    '-modified_time').prefetch_related(
                    'quotas').prefetch_related(
                    'quotas', 'investigators', 'institutions',
                    'publications', 'grants')]


class BaseAllocationView(UpdateView):
    model = AllocationRequest
    form_class = AllocationRequestForm
    page_title = "Update"

    # quota
    formset_quota_class = inlineformset_factory(
        AllocationRequest, Quota, form=QuotaForm, extra=0, can_delete=False)

    # investigator
    formset_investigator_class = inlineformset_factory(
        AllocationRequest, ChiefInvestigator, form=ChiefInvestigatorForm,
        extra=0)

    # institution
    formset_institution_class = inlineformset_factory(
        AllocationRequest, Institution, form=InstitutionForm, extra=0)

    # publication
    formset_publication_class = inlineformset_factory(
        AllocationRequest, Publication, form=PublicationForm, extra=0)

    # grant
    formset_grant_class = inlineformset_factory(
        AllocationRequest, Grant, form=GrantForm, extra=0)

    # The attribute used to record who did the edit.  this should
    # either be approver_email or contact_email
    editor_attr = 'approver_email'

    def __init__(self, **kwargs):
        super(BaseAllocationView, self).__init__(**kwargs)
        # quota
        FormSet_Quota_Class = self.get_formset_quota_class()
        if FormSet_Quota_Class:
            self.formset_quota_tmpl = loader.render_to_string(
                'rcallocation/quota_form.html',
                {'quota_form': FormSet_Quota_Class().empty_form})
        else:
            self.formset_quota_tmpl = ""

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

    def get_formset_quota_class(self):
        return self.formset_quota_class

    def get_formset_investigator_class(self):
        return self.formset_investigator_class

    def get_formset_institution_class(self):
        return self.formset_institution_class

    def get_formset_publication_class(self):
        return self.formset_publication_class

    def get_formset_grant_class(self):
        return self.formset_grant_class

    def get_formset(self, formset):
        kwargs = {'instance': self.object}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return formset(**kwargs)

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

        # quota
        if self.formset_quota_tmpl:
            kwargs['quotaFormTmpl'] = self.formset_quota_tmpl
        storage_zones = json.dumps(
            getattr(settings, 'ALLOCATION_QUOTA_AZ_CHOICES', {}))
        storage_units = json.dumps(
            getattr(settings, 'ALLOCATION_QUOTA_UNITS', {}))
        return (super(BaseAllocationView, self)
                .get_context_data(storage_zones=storage_zones,
                                  storage_units=storage_units,
                                  **kwargs))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object:
            # check the chief investigator
            investigators = self.object.investigators.all()
            if not investigators:
                self.formset_investigator_class = inlineformset_factory(
                    AllocationRequest, ChiefInvestigator,
                    form=ChiefInvestigatorForm, extra=1)
            # check the institutions
            institutions = self.object.institutions.all()
            # not institution existed, we just create a empty one
            if not institutions:
                self.formset_institution_class = inlineformset_factory(
                    AllocationRequest, Institution, form=InstitutionForm,
                    extra=1)

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        kwargs = {'form': form}
        # quota
        formset_quota_class = self.get_formset_quota_class()
        if formset_quota_class:
            kwargs['quotaFormSet'] = self.get_formset(formset_quota_class)

        # investigator
        formset_investigator_class = self.get_formset_investigator_class()
        if formset_investigator_class:
            kwargs['investigatorFormSet'] = self.get_formset(
                formset_investigator_class)

        # institution
        formset_institution_class = self.get_formset_institution_class()
        if formset_institution_class:
            kwargs['institutionFormSet'] = self.get_formset(
                formset_institution_class)

        # publication
        formset_publication_class = self.get_formset_publication_class()
        if formset_publication_class:
            kwargs['publicationFormSet'] = self.get_formset(
                formset_publication_class)

        # grant
        formset_grant_class = self.get_formset_grant_class()
        if formset_grant_class:
            kwargs['grantFormSet'] = self.get_formset(formset_grant_class)
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        kwargs = {'form': form}

        formset_quota_class = self.get_formset_quota_class()
        if formset_quota_class:
            kwargs['quotaFormSet'] = self.get_formset(formset_quota_class)

        formset_investigator_class = self.get_formset_investigator_class()
        if formset_investigator_class:
            kwargs['investigatorFormSet'] = self.get_formset(
                formset_investigator_class)

        formset_institution_class = self.get_formset_institution_class()
        if formset_institution_class:
            kwargs['institutionFormSet'] = self.get_formset(
                formset_institution_class)

        formset_publication_class = self.get_formset_publication_class()
        if formset_publication_class:
            kwargs['publicationFormSet'] = self.get_formset(
                formset_publication_class)

        formset_grant_class = self.get_formset_grant_class()
        if formset_grant_class:
            kwargs['grantFormSet'] = self.get_formset(formset_grant_class)

        if all(map(methodcaller('is_valid'), kwargs.values())):
            return self.form_valid(**kwargs)
        else:
            return self.form_invalid(**kwargs)

    @transaction.atomic
    def form_valid(self, form, quotaFormSet=None, investigatorFormSet=None,
                   institutionFormSet=None, publicationFormSet=None,
                   grantFormSet=None):
        # Create a new historical object based on the original.
        if self.object:
            old_object = AllocationRequest.objects.get(id=self.object.id)
            old_object.parent_request = self.object
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

            object = self.object

        # Save the changes to the request.
        object = form.save(commit=False)
        assert self.editor_attr
        if not object.created_by:
            object.created_by = self.request.user.token.tenant['id']

        # Set the editor attribute
        setattr(object, self.editor_attr, self.request.user.username)

        object.save()
        if quotaFormSet:
            quotaFormSet.save()

        if investigatorFormSet:
            investigatorFormSet.save()

        if institutionFormSet:
            institutionFormSet.save()

        if publicationFormSet:
            publicationFormSet.save()

        if grantFormSet:
            grantFormSet.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, quotaFormSet=None, investigatorFormSet=None,
                     institutionFormSet=None, publicationFormSet=None,
                     grantFormSet=None):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, quotaFormSet=quotaFormSet,
                                  investigatorFormSet=investigatorFormSet,
                                  institutionFormSet=institutionFormSet,
                                  publicationFormSet=publicationFormSet,
                                  grantFormSet=grantFormSet))
