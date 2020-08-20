import logging

from django.core.validators import RegexValidator
from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.urls import reverse
from django.utils.safestring import mark_safe
from select2 import forms as select2_forms

from nectar_dashboard.rcallocation.forcodes import FOR_CODES
from nectar_dashboard.rcallocation import models


LOG = logging.getLogger(__name__)

FOR_CHOICES = tuple((k, "%s %s" % (k, v)) for k, v in FOR_CODES.items())


class FORValidationError(Exception):
    pass


class BaseAllocationForm(forms.ModelForm):
    error_css_class = 'has-error'
    ignore_warnings = forms.BooleanField(widget=forms.HiddenInput(),
                                         required=False)
    field_of_research_1 = select2_forms.ChoiceField(
        choices=FOR_CHOICES,
        widget_kwargs={'choices': FOR_CHOICES,
                       'attrs' : {'class': 'col-md-2'}},
        overlay="Enter a 2, 4 or 6 digit FoR code",
        sortable=True
    )
    field_of_research_2 = select2_forms.ChoiceField(
        choices=FOR_CHOICES,
        widget_kwargs={'choices': FOR_CHOICES,
                       'attrs' : {'class': 'col-md-2'}},
        overlay="Enter a 2, 4 or 6 digit FoR code",
        sortable=True
    )
    field_of_research_3 = select2_forms.ChoiceField(
        choices=FOR_CHOICES,
        widget_kwargs={'choices': FOR_CHOICES,
                       'attrs' : {'class': 'col-md-2'}},
        overlay="Enter a 2, 4 or 6 digit FoR code",
        sortable=True
    )

    class Meta:
        model = models.AllocationRequest
        exclude = ('status', 'created_by', 'submit_date', 'approver_email',
                   'start_date', 'end_date', 'modified_time', 'parent_request',
                   'associated_site', 'provisioned',
                   'project_id', 'notes', 'notifications')

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
            'use_case': forms.Textarea(attrs={'class': 'col-md-6',
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
            'nectar_support': forms.TextInput(attrs={'class': 'col-md-12'}),
            'ncris_support': forms.TextInput(attrs={'class': 'col-md-12'}),
        }

    groups = (
        ('field_of_research_1', 'for_percentage_1'),
        ('field_of_research_2', 'for_percentage_2'),
        ('field_of_research_3', 'for_percentage_3'),
    )

    def __init__(self, **kwargs):
        super(BaseAllocationForm, self).__init__(**kwargs)
        for field in self.fields.values():
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
        data = self.cleaned_data['project_name']
        if data.startswith('pt-'):
            raise forms.ValidationError("Projects can not start with pt-")

        return data

    def clean(self):
        cleaned_data = super(BaseAllocationForm, self).clean()
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
            RegexValidator(regex=r'^[a-zA-Z][-_a-zA-Z0-9]{1,31}$',
                           message='Letters, numbers, underscore and '
                                   'hyphens only. Must start with a letter.')],
        max_length=32,
        label='Project Identifier',
        required=True,
        help_text='A short name used to identify your project. '
                  'The name should contain letters, numbers, underscores and '
                  'hyphens only, must start with a letter and be between than '
                  '5 and 32 characters in length.',
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

    def clean(self):
        cleaned_data = super(AllocationRequestForm, self).clean()
        if 'project_name' in self._errors:
            return cleaned_data

        allocations = models.AllocationRequest.objects.filter(
            project_name=cleaned_data['project_name'],
            parent_request_id=None)

        project_id = None

        if self.instance:
            allocations = allocations.exclude(pk=self.instance.pk)
            project_id = self.instance.project_id

        # Only want this restriction on new allocations only
        if not project_id:
            if len(cleaned_data.get('project_name')) < 5:
                self.add_error(
                    'project_name',
                    forms.ValidationError('Project identifier must be at '
                                          'least 5 characters in length.'))

        if allocations:
            self.add_error(
               'project_name',
               forms.ValidationError(mark_safe(
                    'That project identifier already exists. If your '
                    'allocation has been approved already, please go'
                    ' <a href="%s">here</a> '
                    'to amend it. Otherwise, choose a different identifier.'
                    % reverse('horizon:allocation:user_requests:index'))))

        return cleaned_data


class AllocationAmendRequestForm(BaseAllocationForm):
    class Meta(BaseAllocationForm.Meta):
        pass


class BaseQuotaForm(forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = models.Quota
        fields = '__all__'

        widgets = {
            'resource': forms.HiddenInput(),
        }

    def __init__(self, **kwargs):
        super(BaseQuotaForm, self).__init__(**kwargs)
        inst = kwargs.get('instance', None)
        if inst:
            self.res = inst.resource
        else:
            self.res = self.initial.get('resource')
        if self.res and self.res.resource_type == models.Resource.BOOLEAN:
            self.fields['requested_quota'].widget = IntegerCheckboxInput(
                attrs={'data-toggle': 'toggle'})


def int_bool_check(v):
    return not (v is False or v == 0 or v == '0' or v is None or v == '')


class IntegerCheckboxInput(forms.CheckboxInput):

    def __init__(self, attrs=None, check_test=None):
        super(IntegerCheckboxInput, self).__init__(
            attrs, check_test=int_bool_check)

    def value_from_datadict(self, data, files, name):
        value = super(IntegerCheckboxInput, self).value_from_datadict(data,
                                                                      files,
                                                                      name)
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
        super(QuotaForm, self).__init__(**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')
        self.fields['group'].required = False
        inst = kwargs.get('instance', None)
        if inst and inst.quota:
            allocation = inst.group.allocation
            if allocation.status == models.AllocationRequest.APPROVED:
                self.initial['requested_quota'] = inst.quota


class BaseQuotaGroupForm(forms.ModelForm):

    error_css_class = 'has-error'

    enabled = forms.BooleanField(required=False, widget=forms.HiddenInput(
        attrs={'class': 'quota-group-enabled'}))

    def __init__(self, **kwargs):
        self.service_type = kwargs.pop('service_type')
        super(BaseQuotaGroupForm, self).__init__(**kwargs)

    class Meta:
        model = models.QuotaGroup
        exclude = ('allocation',)


class QuotaGroupForm(BaseQuotaGroupForm):

    def __init__(self, **kwargs):
        super(QuotaGroupForm, self).__init__(**kwargs)
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
        cleaned_data = super(QuotaGroupForm, self).clean()
        enabled = cleaned_data.get('enabled')
        zone = cleaned_data.get('zone')
        if enabled and not zone:
            raise forms.ValidationError("Please specify a zone")


# Base ModelForm
class NectarBaseModelForm(forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        exclude = ('allocation_request',)


# ChiefInvestigatorForm
class ChiefInvestigatorForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = models.ChiefInvestigator
        widgets = {
            'additional_researchers': forms.Textarea(
                attrs={'style': 'height:120px; width:420px'}),
        }

    def __init__(self, **kwargs):
        super(ChiefInvestigatorForm, self).__init__(**kwargs)
        # make sure the empty is not permitted
        self.empty_permitted = False
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')


class InstitutionForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = models.Institution

    def __init__(self, **kwargs):
        super(InstitutionForm, self).__init__(**kwargs)
        # make sure the empty is not permitted
        self.empty_permitted = False
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')


class PublicationForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = models.Publication

    def __init__(self, **kwargs):
        super(PublicationForm, self).__init__(**kwargs)
        # make sure the empty is not permitted
        self.empty_permitted = False
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')


class GrantForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = models.Grant

    def __init__(self, **kwargs):
        super(GrantForm, self).__init__(**kwargs)
        # make sure the empty is not permitted
        self.empty_permitted = False
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')
