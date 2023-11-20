from django import forms

from nectar_dashboard.rcallocation import forms as base_forms
from nectar_dashboard.rcallocation import models


class AllocationApproveForm(forms.ModelForm, base_forms.QuotaMixin):
    has_quotas = True
    error_css_class = 'has-error'
    ignore_warnings = forms.BooleanField(widget=forms.HiddenInput(),
                                         required=False)

    class Meta:
        model = models.AllocationRequest
        fields = (
            'project_name', 'project_description',
            'estimated_project_duration', 'status_explanation',
            'associated_site', 'national', 'special_approval',
            'bundle',
        )

        widgets = {
            'project_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'project_description': forms.TextInput(
                attrs={'readonly': 'readonly'}),
            'associated_site': forms.Select(attrs={'class': 'col-md-6'}),
            'national': forms.CheckboxInput(
                attrs={'class': 'col-md-6',
                       'style': 'height:20px; width:20px'}),
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                'form-control ' + field.widget.attrs.get('class', ''))

        self.generate_quota_fields()

        if self.instance.bundle:
            self.fields['bundle'].required = True

        self.fields['status_explanation'].help_text = 'Reviewer Comment'
        self.fields['status_explanation'].label = 'Comment'
        self.initial['status_explanation'] = ''
        self.fields['associated_site'].required = True
        self.fields['associated_site'].help_text = \
            '''The Approver will normally set the Associated Site to their
            own node.'''
        self.fields['associated_site'].queryset = \
            models.Site.objects.filter(enabled=True)
        self.fields['national'].help_text = \
            '''The Approver should check 'National funding' for all allocations
            that meet the Nectar national funding criteria.'''

        self.instance.status = 'A'

        for name, field in self.fields.items():
            if 'readonly' in field.widget.attrs:
                field.disabled = True


class AllocationRejectForm(forms.ModelForm):
    has_quotas = False
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


class EditNotesForm(forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = models.AllocationRequest
        fields = ('notes',)
