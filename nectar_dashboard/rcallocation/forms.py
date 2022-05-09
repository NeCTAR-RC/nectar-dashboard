import json
import logging
import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.models import ModelChoiceIterator
from django.urls import reverse
from django.utils.safestring import mark_safe

from select2 import fields as select2_fields
from select2 import forms as select2_forms

from nectar_dashboard.rcallocation import forcodes
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import utils


LOG = logging.getLogger(__name__)

FOR_CODES = forcodes.FOR_CODES[forcodes.FOR_SERIES]
FOR_CHOICES = tuple((k, "%s %s" % (k, v))
                    for k, v in FOR_CODES.items())


class FORValidationError(Exception):
    pass


class FoRChoiceField(select2_forms.ChoiceField):
    def __init__(self, label):
        super().__init__(
            label=label,
            choices=FOR_CHOICES,
            widget_kwargs={'choices': FOR_CHOICES,
                           'attrs': {'class': 'col-md-2'}},
            overlay=f"Enter a 2, 4 or 6 digit {forcodes.FOR_SERIES} FoR code",
            sortable=True,
            required=False)


class UsageFieldWidget(forms.CheckboxSelectMultiple):
    option_template_name = 'rcallocation/usage_type.html'


class NCRISChoiceField(select2_fields.ModelMultipleChoiceField):

    def label_from_instance(self, facility):
        return "%s - %s" % (facility.short_name, facility.name)


# This is used in the ARDCChoiceField's superclass to map the simple
# list of ARDCSupport choices to a tree of choices.  When this is used
# with a widget that renders an HTML <select>, it leads to a tree of
# <optgroup>s containing an <option> for each choice.
#
# Refer to the django documentation for details.
class ARDCSupportChoiceIterator(ModelChoiceIterator):

    def label_from_instance(self, support):
        return "%s - %s" % (support.short_name, support.name)

    def __iter__(self):
        # In the results of this iteration, the choices are assembled
        # into lists with the same value in the 'rank' field, with
        # the smallest ranked list first.  Within the lists, the choices
        # are in ascending order of their 'short_name' values.  We
        # use minuses to get markers in the resulting option display.
        # (They are typically the labels for the <optgroup> elements.)
        #
        # Refer to the django documentation and the widget code if you
        # need to understand how this iterator is actually used.
        same_rank = []
        rank = -1
        for s in self.queryset.order_by('rank', 'short_name'):
            if s.rank != rank:
                yield ('------------', same_rank)
                same_rank = []
                rank = s.rank
            same_rank.append((s.short_name, self.label_from_instance(s)))
        if len(same_rank):
            yield ('------------', same_rank)


class ARDCChoiceField(select2_fields.ModelMultipleChoiceField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         queryset=models.ARDCSupport.objects.filter(
                             enabled=True),
                         choice_iterator_cls=ARDCSupportChoiceIterator,
                         **kwargs)


class BaseAllocationForm(forms.ModelForm):
    error_css_class = 'has-error'
    ignore_warnings = forms.BooleanField(widget=forms.HiddenInput(),
                                         required=False)
    field_of_research_1 = FoRChoiceField("First Field Of Research")
    field_of_research_2 = FoRChoiceField("Second Field Of Research")
    field_of_research_3 = FoRChoiceField("Third Field Of Research")

    usage_types = forms.ModelMultipleChoiceField(
        help_text="""Select one or more items that best describe what
                     you are using the Nectar Research Cloud for.  If
                     you select 'Other', include relevant details in the
                     'Proposed Cloud Usage' textbox.
        """,
        error_messages={'required': 'Please check one or more of the above'},
        queryset=models.UsageType.objects.filter(enabled=True),
        widget=UsageFieldWidget(attrs={'class': 'form-inline list-unstyled'}),
        to_field_name='name')

    ardc_support = ARDCChoiceField(
        name='ardc_support',
        model=models.ARDCSupport,
        label="ARDC program or project supporting this request",
        help_text="""ARDC and its predecessor organizations have provided
                     direct funding for a number of projects under various
                     programs.  If this allocation request supports one of
                     these ARDC funded projects or an ARDC-internal project,
                     select the most specific item or items from the menu.
                     If this is a "program", please include the (official)
                     ARDC project name in the "ARDC Support details" field.
        """,
        required=False,
        overlay="Enter an ARDC project or program name",
        to_field_name='short_name')

    ncris_facilities = NCRISChoiceField(
        name='ncris_facilities',
        model=models.NCRISFacility,
        label="NCRIS Facilities supporting this request",
        help_text="""Include any NCRIS Facilities where the facility management
                     actively supports this request in furtherance of its
                     goals.  For example, the resources may requested be to
                     enable a project that the NCRIS Facility is funding, or
                     they may be for infrastructure for the Facility itself.
                     If a NCRIS Facility is not a listed option, select the
                     "Other" option and elaborate in the Explanation field
                     below.  Please do not record ARDC support here.
        """,
        required=False,
        queryset=models.NCRISFacility.objects.all(),
        overlay="Enter an NCRIS Facility name",
        to_field_name='short_name')

    class Meta:
        model = models.AllocationRequest
        exclude = ('status', 'created_by', 'submit_date', 'approver_email',
                   'start_date', 'end_date', 'modified_time', 'parent_request',
                   'associated_site', 'special_approval',
                   'provisioned', 'managed',
                   'project_id', 'notes', 'notifications', 'ncris_support',
                   'nectar_support'
        )

        widgets = {
            'status_explanation': forms.Textarea(
                attrs={'class': 'col-md-6',
                       'style': 'height:120px; width:420px'}),
            'estimated_project_duration': forms.Select(
                attrs={'class': 'col-md-6'}),
            'convert_trial_project': forms.Select(
                attrs={'class': 'col-md-6'},
                choices=[
                    (False, 'No, start with a blank project.'),
                    (True, 'Yes, move resources from my pt- project to '
                           'this new project.'),
                ]),
            'project_name': forms.TextInput(attrs={'class': 'col-md-12'}),
            'contact_email': forms.TextInput(attrs={'readonly': 'readonly'}),
            'use_case': forms.Textarea(
                attrs={'class': 'col-md-6',
                       'style': 'height:120px; width:420px'}),
            'usage_patterns': forms.Textarea(
                attrs={'class': 'col-md-6',
                       'style': 'height:120px; width:420px'}),
            'associated_site': forms.CheckboxInput(
                attrs={'class': 'col-md-6'}),
            'national': forms.CheckboxInput(attrs={'class': 'col-md-6'}),
            'geographic_requirements': forms.Textarea(
                attrs={'class': 'col-md-6',
                       'style': 'height:120px; width:420px'}),
            'for_percentage_1': forms.Select(attrs={'class': 'col-md-2'}),
            'for_percentage_2': forms.Select(attrs={'class': 'col-md-2'}),
            'for_percentage_3': forms.Select(attrs={'class': 'col-md-2'}),
            'ncris_explanation': forms.TextInput(attrs={'class': 'col-md-12'}),
            'ardc_explanation': forms.TextInput(attrs={'class': 'col-md-12'}),
        }

    groups = (
        ('field_of_research_1', 'for_percentage_1'),
        ('field_of_research_2', 'for_percentage_2'),
        ('field_of_research_3', 'for_percentage_3'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field in self.fields.values():
            if field != self.fields['usage_types']:
                field.widget.attrs['class'] = (
                   'form-control ' + field.widget.attrs.get('class', ''))
        self.warnings = []

    def _in_groups(self, field):
        for group in self.groups:
            if field.name in group:
                return True
        return False

    def visible_fields(self):
        return [field for field in self
                if (not field.is_hidden
                    and not self._in_groups(field))]

    def grouped_fields(self):
        grouped_fields = []
        for grouping in self.groups:
            grouped_fields.append([f for f in self if f.name in grouping])
        return grouped_fields

    def _clean_form(self):
        try:
            self.cleaned_data = self.clean()
        except FORValidationError as e:
            self._errors['FOR_ERRORS'] = self.error_class([e])
        except forms.ValidationError as e:
            self._errors[NON_FIELD_ERRORS] = self.error_class([e])

    def get_for_errors(self):
        return self._errors.get('FOR_ERRORS', [])

    def clean_project_name(self):
        # There are stricter validations implemented in the
        # AllocationRequestForm class.
        data = self.cleaned_data['project_name']
        if data and data.startswith('pt-'):
            raise forms.ValidationError(
                "Project names cannot start with 'pt-'")
        return data

    def clean(self):
        cleaned_data = super().clean()
        ardc_explanation = self.cleaned_data['ardc_explanation']
        ncris_explanation = self.cleaned_data['ncris_explanation']
        supports = self.cleaned_data['ardc_support']
        facilities = self.cleaned_data['ncris_facilities']

        if ardc_explanation and not len(supports):
            self.add_error('ardc_explanation',
                           "No ARDC projects or programs have been selected: "
                           "choose one or more, or remove the explanation "
                           "text.")
        elif not ardc_explanation and \
             any(s.explain for s in supports):
            self.add_error('ardc_explanation',
                           "Add details for the ARDC support that you "
                           "are claiming for your request.")

        if ncris_explanation and not len(facilities):
            self.add_error('ncris_explanation',
                           "No NCRIS Facilities have been selected: "
                           "choose one or more, or remove the explanation "
                           "text.")
        elif not ncris_explanation and \
             any(f.short_name in ('Other', 'Pilot') for f in facilities):
            self.add_error('ncris_explanation',
                           "More details are required when you include "
                           "'Pilot' or 'Other' above.")

        fors = []
        for for_name, perc_name in self.groups:
            perc = cleaned_data.get(perc_name)
            FOR = cleaned_data.get(for_name)
            if not FOR and not perc:
                continue
            if FOR and perc == 0:
                raise FORValidationError(
                    "Percentage for Field Of Research '%s' cannot be 0" % FOR)

            if not FOR and perc > 0:
                raise FORValidationError(
                    "Percentage set for unspecified Field Of Research")
            fors.append(perc)

        for_sum = sum(fors)
        if for_sum > 100:
            raise FORValidationError(
                "Sum of Field Of Research percentages greater than 100")

        return cleaned_data


class AllocationRequestForm(BaseAllocationForm):

    project_name = forms.CharField(
        validators=[
            RegexValidator(regex=r'^[a-zA-Z][-_a-zA-Z0-9]+$',
                           message='Letters, numbers, underscore and '
                                   'hyphens only. Must start with a letter.'),
            RegexValidator(regex=r'^.{5,32}$',
                           message='Between 5 and 32 characters required.'),
            RegexValidator(regex=r'^pt[_-].*$',
                           inverse_match=True, flags=re.I,
                           message='Must not start with "pt-" or similar.')],
        max_length=32,
        label='Project Identifier',
        required=True,
        help_text='A short name used to identify your project. '
                  'The name should contain letters, numbers, underscores and '
                  'hyphens only, must start with a letter and be between than '
                  '5 and 32 characters in length.',
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

    def clean(self):
        cleaned_data = super().clean()
        project_name = cleaned_data.get('project_name')

        if project_name and not self.instance.id:
            # Only want this restriction on new allocations only
            if len(project_name) < 5:
                self.add_error(
                    'project_name',
                    forms.ValidationError('Project identifier must be at '
                                          'least 5 characters in length.'))

            if not utils.is_project_name_available(project_name):
                self.add_error(
                   'project_name',
                   forms.ValidationError(mark_safe(
                        'That project identifier already exists. If your '
                        'allocation has been approved already, please go'
                        ' <a href="%s">here</a> '
                        'to amend it. '
                        'Otherwise, choose a different identifier.'
                        % reverse('horizon:allocation:user_requests:index'))))

        return cleaned_data


class AllocationAmendRequestForm(BaseAllocationForm):
    class Meta(BaseAllocationForm.Meta):
        pass


class BaseQuotaForm(forms.ModelForm):
    error_css_class = 'has-error'
    quota = forms.IntegerField(min_value=0, required=False)
    requested_quota = forms.IntegerField(min_value=0, required=False)

    class Meta:
        model = models.Quota
        fields = '__all__'

        widgets = {
            'resource': forms.HiddenInput(),
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        inst = kwargs.get('instance', None)
        if inst:
            self.resource = inst.resource
        else:
            self.resource = self.initial.get('resource')
        if (self.resource
                and self.resource.resource_type == models.Resource.BOOLEAN):
            self.fields['requested_quota'].widget = IntegerCheckboxInput(
                attrs={'data-toggle': 'toggle'})


def int_bool_check(v):
    return not (v is False or v == 0 or v == '0' or v is None or v == '')


class IntegerCheckboxInput(forms.CheckboxInput):

    def __init__(self, attrs=None, check_test=None):
        super().__init__(
            attrs, check_test=int_bool_check)

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        return int(value)


class QuotaForm(BaseQuotaForm):
    """This version of the form class that allows editing of the requested
    quota values.  If the allocation record being edited is in approved
    state, we pre-fill the requested quota values from the current quota
    values.
    """

    class Meta(BaseQuotaForm.Meta):
        model = models.Quota
        exclude = ('quota',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')
        self.fields['group'].required = False
        inst = kwargs.get('instance', None)
        if inst and inst.quota:
            allocation = inst.group.allocation
            if allocation.status == models.AllocationRequest.APPROVED:
                self.initial['requested_quota'] = inst.quota

        if self.resource and self.resource.default:
            if self.initial.get('requested_quota', 0) < self.resource.default:
                self.initial['requested_quota'] = self.resource.default

    def has_changed(self):
        if self.resource and self.resource.default:
            return True
        return super().has_changed()


class BaseQuotaGroupForm(forms.ModelForm):

    error_css_class = 'has-error'

    enabled = forms.BooleanField(required=False, widget=forms.HiddenInput(
        attrs={'class': 'quota-group-enabled'}))

    def __init__(self, **kwargs):
        self.service_type = kwargs.pop('service_type')
        super().__init__(**kwargs)

    class Meta:
        model = models.QuotaGroup
        exclude = ('allocation',)


class QuotaGroupForm(BaseQuotaGroupForm):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['service_type'].widget = forms.HiddenInput()
        self.fields['service_type'].initial = self.service_type
        self.fields['zone'].required = False
        self.fields['zone'].queryset = \
            self.service_type.zones.filter(enabled=True)
        if len(self.service_type.zones.all()) == 1:
            self.fields['zone'].widget = forms.HiddenInput()
            self.fields['zone'].initial = 'nectar'
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + ' form-control')

    def clean(self):
        cleaned_data = super().clean()
        enabled = cleaned_data.get('enabled')
        zone = cleaned_data.get('zone')
        if enabled and not zone:
            raise forms.ValidationError("Please specify a zone")


class NectarBaseModelForm(forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        exclude = ('allocation_request',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # make sure that empty is not permitted
        self.empty_permitted = False
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + ' form-control')


class ChiefInvestigatorForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = models.ChiefInvestigator
        widgets = {
            'additional_researchers': forms.Textarea(
                attrs={'style': 'height:120px; width:420px'}),
        }


class InstitutionForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = models.Institution


DOI_PROTOCOL_PATTERN = re.compile("(?i)^doi:(.+)$")
DOI_PROTOCOL_PATTERN_2 = re.compile("(?i)^https?:[a-z0-9./_\\-]+?/(10\\..+)$")


class PublicationForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = models.Publication
        widgets = {
            'publication': forms.Textarea(
                attrs={'style': 'height:120px; width:420px'}),
            'doi': forms.TextInput(
                attrs={'style': 'width:420px'}),
            'crossref_metadata': forms.HiddenInput()
        }

    def clean_doi(self):
        # Quietly strip off a "doi:" prefix or resolver URL if provided.
        doi = self.cleaned_data['doi']
        if doi:
            match = DOI_PROTOCOL_PATTERN.match(doi)
            if match:
                return match.group(1)
            match = DOI_PROTOCOL_PATTERN_2.match(doi)
            if match:
                return match.group(1)
            else:
                return doi
        else:
            return ''

    def clean(self):
        cleaned_data = super().clean()
        doi = cleaned_data.get('doi', '')
        publication = cleaned_data.get('publication', '')
        crossref_metadata = cleaned_data.get('crossref_metadata', '')
        if not doi and not publication:
            self.add_error(None,
                           ValidationError('No details about this research '
                                           'output have been provided. '
                                           'Provide either a DOI or other '
                                           'details, as appropriate.'))
        if doi and not crossref_metadata and not publication:
            self.add_error('publication',
                           ValidationError('Since the DOI you provided has '
                                           'not been validated, other '
                                           'publication details must be '
                                           'entered by hand.'))
        if crossref_metadata:
            # The field may hidden, but we still don't want it to be populated
            # with garbage, deliberately or by accident.  Make the errors
            # non-field errors so that they get displayed by the template.
            try:
                data = json.loads(crossref_metadata)
                if not isinstance(data, dict) or not data.get('message'):
                    self.add_error(None,
                                   ValidationError('Crossref_metadata not a '
                                                   'proper Crossref response'))
            except json.JSONDecodeError:
                self.add_error(None,
                               ValidationError('Crossref_metadata not JSON'))


class GrantForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = models.Grant

    def clean(self):
        cleaned_data = super().clean()
        grant_type = cleaned_data.get('grant_type', '')
        grant_subtype = cleaned_data.get('grant_subtype', '')
        grant_id = cleaned_data.get('grant_id')
        funding_body_scheme = cleaned_data.get('funding_body_scheme')
        if grant_type == 'arc':
            if not grant_subtype.startswith('arc-'):
                self.add_error(
                    'grant_subtype',
                    ValidationError(
                        'Select an ARC grant subtype for this grant'))
            if not grant_subtype == 'arc-other' and not grant_id:
                self.add_error(
                    'grant_id',
                    ValidationError('Enter the ARC grant id for this grant'))
        elif grant_type == 'nhmrc':
            if not grant_subtype.startswith('nhmrc-'):
                self.add_error(
                    'grant_subtype',
                    ValidationError(
                        'Select an NHMRC grant subtype for this grant'))
            if not grant_subtype == 'nhmrc-other' and not grant_id:
                self.add_error(
                    'grant_id',
                    ValidationError('Enter the NHMRC grant id for this grant'))
        elif grant_type == 'rdc':
            if not grant_subtype.startswith('rdc-'):
                self.add_error(
                    'grant_subtype',
                    ValidationError(
                        'Select an RDC grant subtype for this grant'))
            if not funding_body_scheme and not grant_id:
                self.add_error(
                    'funding_body_scheme',
                    ValidationError('Provide details for this grant '
                                    'or a grant id (below!)'))
        elif grant_type == 'state':
            if grant_subtype not in ['act', 'nsw', 'nt', 'qld',
                                     'sa', 'tas', 'vic', 'wa']:
                self.add_error(
                    'grant_subtype',
                    ValidationError('Select the State for this grant'))
        elif grant_type:
            if grant_subtype != 'unspecified':
                self.add_error(
                    'grant_subtype',
                    ValidationError('Inappropriate subtype for this grant'))

        if grant_type not in ['arc', 'nhmrc', 'rdc', ''] \
           or (grant_type in ['arc', 'nhmrc']
               and grant_subtype.endswith('-other')):
            if not funding_body_scheme:
                self.add_error(
                    'funding_body_scheme',
                    ValidationError('Provide details for this grant'))


class UsageForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = models.UsageType
