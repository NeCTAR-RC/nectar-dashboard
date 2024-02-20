from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.forms.models import ModelChoiceIterator
from django.urls import reverse

from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import views
from select2 import views as select2_views

from nectar_dashboard.rcallocation.request import forms as request_forms


class OrganisationChoiceIterator(ModelChoiceIterator):

    def label_from_instance(self, org):
        if org.short_name:
            return f"{org.full_name} - {org.short_name} ({org.country})"
        else:
            return f"{org.full_name} ({org.country})"

    def __iter__(self):
        for o in self.queryset:
            yield (o.id, self.label_from_instance(o))


def organisation_filter_mapper(filter_arg, user=None):
    if filter_arg == 'world':
        q = None
    elif filter_arg == 'anz':
        q = Q(country__in=['au', 'nz'])
    elif filter_arg == 'world-single':
        q = ~Q(full_name=models.ORG_ALL_FULL_NAME)
    elif filter_arg == 'anz-single':
        q = Q(country__in=['au', 'nz']) \
            & ~Q(full_name=models.ORG_ALL_FULL_NAME)
    else:
        raise select2_views.InvalidParameter(
            f"Unrecognized filter '{filter_arg}'")
    if user is not None:
        # Filter out unvetted proposals apart from those proposed by
        # the user filling out the form
        qq = (~Q(ror_id="") | Q(vetted_by__isnull=False)
              | Q(proposed_by=user.username))
        q = q & qq if q else qq
    return q


def fetch_organisations(request):
    view = select2_views.Select2View(
        request, 'rcallocation', 'allocationrequest',
        'supported_organisations',
        choice_iterator_cls=OrganisationChoiceIterator,
        fetch_filter_mapper=organisation_filter_mapper)
    return view.fetch_items()


def init_organisations(request):
    view = select2_views.Select2View(
        request, 'rcallocation', 'allocationrequest',
        'supported_organisations',
        choice_iterator_cls=OrganisationChoiceIterator,
        fetch_filter_mapper=organisation_filter_mapper)
    return view.init_selection()


class AllocationCreateView(views.BaseAllocationView):
    template_name = "rcallocation/allocationrequest_edit.html"
    form_class = request_forms.UserAllocationRequestForm
    editor_attr = 'contact_email'
    page_title = 'Allocation Request'

    formset_investigator_class = inlineformset_factory(
        models.AllocationRequest, models.ChiefInvestigator,
        form=forms.ChiefInvestigatorForm, extra=1)

    def get_object(self):
        return None

    def get_initial(self):
        initial = super().get_initial()
        initial['contact_email'] = self.request.user.username
        return initial

    def get_success_url(self):
        return reverse('horizon:allocation:user_requests:index')

    def test_func(self):
        return True
