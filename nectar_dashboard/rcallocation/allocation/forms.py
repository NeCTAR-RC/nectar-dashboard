from django.forms import ModelForm, Textarea, TextInput, Select, NumberInput

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import forms


class AllocationApproveForm(ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = models.AllocationRequest
        fields = (
            'project_name', 'project_description', 'start_date',
            'estimated_project_duration', 'cores', 'instances',
            'core_quota', 'instance_quota', 'status_explanation',
            'funding_national_percent', 'funding_node',
        )

        exclude = ('ram_quota', 'nectar_support', 'ncris_support',)

        widgets = {
            'project_name': TextInput(attrs={'readonly': 'readonly'}),
            'project_description': TextInput(attrs={'readonly': 'readonly'}),
            'start_date': TextInput(attrs={'readonly': 'readonly'}),
            'status_explanation': Textarea(
                attrs={'class': 'col-md-6 form-control',
                       'style': 'height:120px; width:420px'}),
            'funding_national_percent': NumberInput(
                attrs={'class': 'form-control col-md-2'}),
            'funding_node': Select(attrs={'class': 'col-md-6'}),

        }

    def __init__(self, **kwargs):
        super(AllocationApproveForm, self).__init__(**kwargs)
        self.fields['project_name'].widget.attrs['class'] = 'form-control'
        self.fields['project_description'].widget.attrs[
            'class'] = 'form-control'
        self.fields['project_description'].required = False
        self.fields['start_date'].widget.attrs['class'] = 'form-control'
        self.fields['start_date'].widget.attrs['style'] = 'border-radius:0;'
        self.fields['start_date'].required = False
        self.fields['estimated_project_duration'].widget.attrs[
            'class'] = 'form-control'
        self.fields['estimated_project_duration'].widget.attrs[
            'readonly'] = True
        self.fields['estimated_project_duration'].required = False
        self.fields['cores'].widget.attrs['readonly'] = True
        self.fields['cores'].widget.attrs['class'] = 'form-control'
        self.fields['cores'].help_text = ''
        self.fields['cores'].label = 'Requested cores'
        self.fields['cores'].required = False
        self.fields['instances'].widget.attrs['readonly'] = True
        self.fields['instances'].widget.attrs['class'] = 'form-control'
        self.fields['instances'].help_text = ''
        self.fields['instances'].label = 'Requested instances'
        self.fields['instances'].required = False
        self.fields['status_explanation'].required = False
        self.fields['status_explanation'].help_text = 'Reviewer Comment'
        self.fields['status_explanation'].label = 'Comment'
        self.fields['instance_quota'].widget.attrs['class'] = 'form-control'
        self.fields['core_quota'].widget.attrs['class'] = 'form-control'
        self.initial['core_quota'] = self.instance.cores
        self.initial['instance_quota'] = self.instance.instances
        self.initial['ram_quota'] = self.instance.cores * 4
        self.initial['status_explanation'] = ''
        self.fields['funding_national_percent'].required = True
        self.fields['funding_node'].required = False
        self.fields['funding_node'].widget.attrs['class'] = 'form-control'

        if self.instance.status == 'L':
            self.instance.status = 'M'
        else:
            self.instance.status = 'A'

    def clean_ram_quota(self):
        return self.cleaned_data['core_quota'] * 4


class AllocationRejectForm(ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = models.AllocationRequest
        fields = ('project_name', 'project_description', 'status_explanation',)
        widgets = {
            'project_name': TextInput(attrs={'class': 'form-control col-md-6',
                                             'readonly': 'readonly'}),
            'project_description': TextInput(
                attrs={'class': 'form-control col-md-6',
                       'readonly': 'readonly'}),
            'status_explanation': Textarea(
                attrs={'class': 'form-control col-md-6',
                       'style': 'height:120px; width:420px'})
        }

    def __init__(self, **kwargs):
        super(AllocationRejectForm, self).__init__(**kwargs)
        if self.instance.status == 'L':
            self.instance.status = 'O'
            self.fields['status_explanation'].required = False
        elif self.instance.status == 'X':
            self.instance.status = 'J'
        else:
            self.instance.status = 'R'
        self.fields['project_description'].required = False


class AllocationProvisionForm(ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = models.AllocationRequest

        fields = ('project_name', 'contact_email', 'start_date',
                  'estimated_project_duration', 'project_description')
        exclude = ('nectar_support', 'ncris_support',
                   'core_quota', 'instance_quota', 'ram_quota', 'project_id')
        widgets = {
            'project_name': TextInput(attrs={'class': 'form-control col-md-6',
                                             'readonly': 'readonly'}),
            'project_description': TextInput(
                attrs={'class': 'form-control col-md-6',
                       'readonly': 'readonly'}),
            'start_date': TextInput(attrs={'class': 'form-control col-md-6',
                                           'readonly': 'readonly',
                                           'style': 'border-radius:0;'}),
            'contact_email': TextInput(attrs={'class': 'form-control col-md-6',
                                              'readonly': 'readonly'}),
            'estimated_project_duration': TextInput(
                attrs={'class': 'form-control col-md-6',
                       'readonly': 'readonly'}),
        }

    def __init__(self, **kwargs):
        super(AllocationProvisionForm, self).__init__(**kwargs)
        read_only_fields = ('project_name', 'contact_email', 'start_date',
                            'estimated_project_duration',)
        for field_name in read_only_fields:
            self.fields[field_name].widget.attrs['readonly'] = True
            self.fields[field_name].required = False

        self.fields['contact_email'].label = 'Project manager'
        self.fields['project_name'].required = False
        self.fields['estimated_project_duration'].label = \
            'Estimated project duration - month(s)'
        self.instance.status = 'P'


class QuotaForm(forms.BaseQuotaForm):
    class Meta(forms.BaseQuotaForm.Meta):
        exclude = ('allocation_request',
                   'units',
                   'resource',
                   'zone')

    def __init__(self, **kwargs):
        super(QuotaForm, self).__init__(**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')
        self.fields['requested_quota'].widget.attrs['readonly'] = True
        self.fields['requested_quota'].required = False
        self.initial['quota'] = self.instance.requested_quota

    def has_changed(self):
        """
        Overriding this, as the initial data passed to the form does not get
        noticed, and so does not get saved, unless it actually changes
        """
        changed_data = super(forms.BaseQuotaForm, self).has_changed()
        return bool(self.initial or changed_data)
