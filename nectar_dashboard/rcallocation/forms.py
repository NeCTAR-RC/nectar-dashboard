from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.forms import ModelForm, ValidationError, BaseInlineFormSet
from django.forms import TextInput, Select, CharField, Textarea, HiddenInput
from django.forms.forms import NON_FIELD_ERRORS
from django.utils.safestring import mark_safe
from nectar_dashboard.rcallocation.models import AllocationRequest, Quota, \
    ChiefInvestigator, Institution, Publication, Grant


class FORValidationError(Exception):
    pass


class BaseAllocationForm(ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = AllocationRequest
        exclude = ('status', 'created_by', 'submit_date', 'approver_email',
                   'modified_time', 'parent_request', 'primary_instance_type',
                   'volume_zone', 'object_storage_zone',
                   'funding_national_percent', 'funding_node', 'provisioned',
                   )
        widgets = {
            'status_explanation': Textarea(
                attrs={'class': 'col-md-6',
                       'style': 'height:120px; width:420px'}),
            'start_date': TextInput(attrs={'class': 'datepicker2 col-md-12',
                                           'style': 'border-radius:0;'}),
            'estimated_project_duration': Select(attrs={'class': 'col-md-6'}),
            'convert_trial_project': Select(
                attrs={'class': 'col-md-6'},
                choices=[
                    (False, 'No, start with a blank project.'),
                    (True, 'Yes, move resources from my pt- project to '
                           'this new project.'),
                ]),
            'project_name': TextInput(attrs={'class': 'col-md-12'}),
            'tenant_uuid': HiddenInput(),
            'contact_email': TextInput(attrs={'readonly': 'readonly'}),
            'use_case': Textarea(attrs={'class': 'col-md-6',
                                        'style': 'height:120px; width:420px'}),
            'usage_patterns': Textarea(
                attrs={'class': 'col-md-6',
                       'style': 'height:120px; width:420px'}),
            'allocation_home': Select(attrs={'class': 'col-md-6'}),
            'geographic_requirements': Textarea(
                attrs={'class': 'col-md-6',
                       'style': 'height:120px; width:420px'}),
            'field_of_research_1': Select(attrs={'class': 'col-md-6'}),
            'field_of_research_2': Select(attrs={'class': 'col-md-6'}),
            'field_of_research_3': Select(attrs={'class': 'col-md-6'}),
            'for_percentage_1': Select(attrs={'class': 'col-md-2'}),
            'for_percentage_2': Select(attrs={'class': 'col-md-2'}),
            'for_percentage_3': Select(attrs={'class': 'col-md-2'}),
            'nectar_support': TextInput(attrs={'class': 'col-md-12'}),
            'ncris_support': TextInput(attrs={'class': 'col-md-12'}),
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

    def _in_groups(self, field):
        for group in self.groups:
            if field.name in group:
                return True
        return False

    def visible_fields(self):
        return [field for field in self
                if (not field.is_hidden and
                    not self._in_groups(field))]

    def grouped_fields(self):
        grouped_fields = []
        for grouping in self.groups:
            grouped_fields.append([f for f in self if f.name in grouping])
        return grouped_fields

    def _clean_form(self):
        try:
            self.cleaned_data = self.clean()
        except FORValidationError as e:
            self._errors['FOR_ERRORS'] = self.error_class([e.message])
        except ValidationError as e:
            self._errors[NON_FIELD_ERRORS] = self.error_class([e.message])

    def get_for_errors(self):
        return self._errors.get('FOR_ERRORS', [])

    def clean_tenant_name(self):
        data = self.cleaned_data['tenant_name']
        if data.startswith('pt-'):
            raise ValidationError("Projects can not start with pt-")

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
    class Meta(BaseAllocationForm.Meta):
        exclude = ('ram_quota', 'instance_quota',
                   'core_quota'
                   ) + BaseAllocationForm.Meta.exclude

    tenant_name = CharField(
        validators=[
            RegexValidator(regex=r'^[a-zA-Z][-_a-zA-Z0-9]{1,31}$',
                           message='Letters, numbers, underscore and '
                                   'hyphens only. Must start with a letter.')],
        max_length=32,
        label='Project Identifier',
        required=True,
        help_text='A short name used to identify your project.<br>'
                  'Letters, numbers, underscores and hyphens only.<br>'
                  'Must start with a letter and be less than 32 characters.',
        widget=TextInput(attrs={'autofocus': 'autofocus'}))

    def clean(self):
        cleaned_data = super(AllocationRequestForm, self).clean()
        if 'tenant_name' in self._errors:
            return cleaned_data

        allocations = (AllocationRequest.objects
                       .filter(tenant_name=cleaned_data['tenant_name'],
                               parent_request_id=None))
        if self.instance:
            allocations = allocations.exclude(pk=self.instance.pk)

        if allocations:
            self._errors["tenant_name"] = \
                [mark_safe(
                    'That project identifier already exists. If your '
                    'allocation has been approved already, please go'
                    ' <a href="%s">here</a> '
                    'to amend it. Otherwise, choose a different identifier.'
                    % reverse('horizon:allocation:user_requests:index'))]
            del cleaned_data["tenant_name"]

        return cleaned_data


class AllocationAmendRequestForm(BaseAllocationForm):
    class Meta(BaseAllocationForm.Meta):
        pass


class BaseQuotaForm(ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = Quota
        fields = '__all__'


class QuotaInlineFormSet(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        zone_resources = []
        for form in self.forms:
            if form.cleaned_data:
                zone = form.cleaned_data['zone']
                resource = form.cleaned_data['resource']
                zr = (zone, resource)
                if zr in zone_resources:
                    quota_zones = dict(
                        getattr(settings, 'ALLOCATION_NECTAR_AZ_CHOICES',
                                tuple()) +
                        getattr(settings, 'ALLOCATION_OBJECT_AZ_CHOICES',
                                tuple()) +
                        getattr(settings, 'ALLOCATION_VOLUME_AZ_CHOICES',
                                tuple()))
                    quota_types = dict(
                        getattr(settings, 'ALLOCATION_QUOTA_TYPES', tuple()))
                    raise forms.ValidationError(
                        'You have a duplicate request for %s in the %s zone. '
                        'Please amend your quota request.' % (
                            quota_types[resource], quota_zones[zone]))
                zone_resources.append(zr)


class QuotaForm(BaseQuotaForm):
    class Meta(BaseQuotaForm.Meta):
        model = Quota
        exclude = ('allocation_request', 'quota')

    zone = forms.ChoiceField()

    def __init__(self, **kwargs):
        super(QuotaForm, self).__init__(**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')
        # Set the storage choices for each quota
        storage_zones = getattr(settings, 'ALLOCATION_QUOTA_AZ_CHOICES', ())
        if 'resource' in self.fields and 'zone' in self.fields:
            if self._raw_value('resource'):
                self.fields['zone']._set_choices(
                    ((u'', u'---------'),) +
                    storage_zones[self._raw_value('resource')])
            elif self.instance.resource:
                self.fields['zone']._set_choices(
                    ((u'', u'---------'),) +
                    storage_zones[self.instance.resource])


# Base ModelForm
class NectarBaseModelForm(ModelForm):
    error_css_class = 'has-error'

    class Meta:
        exclude = ('allocation_request',)


# ChiefInvestigatorForm
class ChiefInvestigatorForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = ChiefInvestigator
        widgets = {
            'additional_researchers': Textarea(
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
        model = Institution

    def __init__(self, **kwargs):
        super(InstitutionForm, self).__init__(**kwargs)
        # make sure the empty is not permitted
        self.empty_permitted = False
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')


class PublicationForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = Publication

    def __init__(self, **kwargs):
        super(PublicationForm, self).__init__(**kwargs)
        # make sure the empty is not permitted
        self.empty_permitted = False
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')


class GrantForm(NectarBaseModelForm):
    class Meta(NectarBaseModelForm.Meta):
        model = Grant

    def __init__(self, **kwargs):
        super(GrantForm, self).__init__(**kwargs)
        # make sure the empty is not permitted
        self.empty_permitted = False
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')
