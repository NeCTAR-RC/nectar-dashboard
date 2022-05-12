from django import forms

from nectar_dashboard.rcallocation import forms as base_forms
from nectar_dashboard.rcallocation import models


class AllocationApproveForm(forms.ModelForm):
    error_css_class = 'has-error'
    ignore_warnings = forms.BooleanField(widget=forms.HiddenInput(),
                                         required=False)

    class Meta:
        model = models.AllocationRequest
        fields = (
            'project_name', 'project_description',
            'estimated_project_duration', 'status_explanation',
            'associated_site', 'national', 'special_approval',
        )

        exclude = ('nectar_support', 'ncris_support',)

        widgets = {
            'project_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'project_description': forms.TextInput(
                attrs={'readonly': 'readonly'}),
            'status_explanation': forms.Textarea(
                attrs={'class': 'form-control'}),
            'special_approval': forms.Textarea(
                attrs={'class': 'form-control'}),
            'associated_site': forms.Select(attrs={'class': 'col-md-6'}),
            'national': forms.CheckboxInput(
                attrs={'class': 'col-md-6 form-control',
                       'style': 'height:20px; width:20px'}),
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['project_name'].widget.attrs['class'] = 'form-control'
        self.fields['project_description'].widget.attrs[
            'class'] = 'form-control'
        self.fields['project_description'].required = False
        self.fields['estimated_project_duration'].widget.attrs[
            'class'] = 'form-control'
        self.fields['estimated_project_duration'].required = False
        self.fields['status_explanation'].required = False
        self.fields['status_explanation'].help_text = 'Reviewer Comment'
        self.fields['status_explanation'].label = 'Comment'
        self.initial['status_explanation'] = ''
        self.fields['associated_site'].required = True
        self.fields['associated_site'].help_text = \
            '''The Approver will normally set the Associated Site to their
            own node.'''
        self.fields['associated_site'].widget.attrs['class'] = 'form-control'
        self.fields['associated_site'].queryset = \
            models.Site.objects.filter(enabled=True)
        self.fields['national'].required = False
        self.fields['national'].help_text = \
            '''The Approver should check 'National funding' for all allocations
            that meet the Nectar national funding criteria.'''

        self.instance.status = 'A'

        for name, field in self.fields.items():
            if 'readonly' in field.widget.attrs:
                field.disabled = True


class AllocationRejectForm(forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = models.AllocationRequest
        fields = ('project_name', 'project_description', 'status_explanation',)
        widgets = {
            'project_name': forms.TextInput(
                attrs={'class': 'form-control',
                       'readonly': 'readonly'}),
            'project_description': forms.TextInput(
                attrs={'class': 'form-control',
                       'readonly': 'readonly'}),
            'status_explanation': forms.Textarea(
                attrs={'class': 'form-control'})
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.instance.status == 'X':
            self.instance.status = 'J'
        else:
            self.instance.status = 'R'
        self.fields['project_description'].required = False


class QuotaForm(base_forms.BaseQuotaForm):
    class Meta(base_forms.BaseQuotaForm.Meta):
        fields = '__all__'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')
        self.fields['requested_quota'].widget.attrs['readonly'] = True
        self.fields['requested_quota'].required = False
        quota = kwargs.pop('instance', None)
        if not quota:
            self.fields['requested_quota'].widget = forms.HiddenInput()
        self.initial['quota'] = self.instance.requested_quota
        if (self.resource
                and self.resource.resource_type == models.Resource.BOOLEAN):
            self.fields['quota'].widget = base_forms.IntegerCheckboxInput(
                attrs={'data-toggle': 'toggle'})

    def has_changed(self):
        """Overriding this, as the initial data passed to the form does not get
        noticed, and so does not get saved, unless it actually changes
        """
        changed_data = super().has_changed()
        return bool(self.initial or changed_data)


class QuotaGroupForm(base_forms.BaseQuotaGroupForm):

    class Meta(base_forms.BaseQuotaGroupForm.Meta):
        widgets = {
            'zone': forms.HiddenInput(),
            'service_type': forms.HiddenInput()
        }


class EditNotesForm(forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = models.AllocationRequest
        fields = ('notes',)
