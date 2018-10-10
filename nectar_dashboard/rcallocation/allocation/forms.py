from django import forms as d_forms

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import forms


class AllocationApproveForm(d_forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = models.AllocationRequest
        fields = (
            'project_name', 'project_description', 'start_date',
            'estimated_project_duration', 'status_explanation',
            'requested_allocation_home', 'allocation_home',
        )

        exclude = ('nectar_support', 'ncris_support',)

        widgets = {
            'project_name': d_forms.TextInput(attrs={'readonly': 'readonly'}),
            'project_description': d_forms.TextInput(
                attrs={'readonly': 'readonly'}),
            'start_date': d_forms.TextInput(attrs={'readonly': 'readonly'}),
            'status_explanation': d_forms.Textarea(
                attrs={'class': 'col-md-6 form-control',
                       'style': 'height:120px; width:420px'}),
            'requested_allocation_home': d_forms.Select(
                attrs={'class': 'col-md-6'}),
            'allocation_home': d_forms.Select(attrs={'class': 'col-md-6'}),

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
        self.fields['status_explanation'].required = False
        self.fields['status_explanation'].help_text = 'Reviewer Comment'
        self.fields['status_explanation'].label = 'Comment'
        self.initial['status_explanation'] = ''
        self.fields['allocation_home'].required = True
        self.fields['allocation_home'].widget.attrs['class'] = 'form-control'
        self.fields['requested_allocation_home'].label = \
                                                'Requested Allocation Home'
        self.fields['requested_allocation_home'].widget.attrs[
            'class'] = 'form-control'
        self.fields['requested_allocation_home'].widget.attrs[
            'readonly'] = True
        self.fields['requested_allocation_home'].widget.attrs[
            'disabled'] = True

        if self.instance.status == 'L':
            self.instance.status = 'M'
        else:
            self.instance.status = 'A'


class AllocationRejectForm(d_forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = models.AllocationRequest
        fields = ('project_name', 'project_description', 'status_explanation',)
        widgets = {
            'project_name': d_forms.TextInput(
                attrs={'class': 'form-control col-md-6',
                       'readonly': 'readonly'}),
            'project_description': d_forms.TextInput(
                attrs={'class': 'form-control col-md-6',
                       'readonly': 'readonly'}),
            'status_explanation': d_forms.Textarea(
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


class QuotaForm(forms.BaseQuotaForm):
    class Meta(forms.BaseQuotaForm.Meta):
        fields = '__all__'

    def __init__(self, **kwargs):
        super(QuotaForm, self).__init__(**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + 'form-control')
        self.fields['requested_quota'].widget.attrs['readonly'] = True
        self.fields['requested_quota'].widget.attrs['disabled'] = True
        self.fields['requested_quota'].required = False
        quota = kwargs.pop('instance', None)
        if not quota:
            self.fields['requested_quota'].widget = d_forms.HiddenInput()
        self.initial['quota'] = self.instance.requested_quota
        if self.res and self.res.resource_type == models.Resource.BOOLEAN:
            self.fields['quota'].widget = forms.IntegerCheckboxInput(
                attrs={'data-toggle': 'toggle'})

    def has_changed(self):
        """
        Overriding this, as the initial data passed to the form does not get
        noticed, and so does not get saved, unless it actually changes
        """
        changed_data = super(forms.BaseQuotaForm, self).has_changed()
        return bool(self.initial or changed_data)


class QuotaGroupForm(forms.BaseQuotaGroupForm):

    class Meta(forms.BaseQuotaGroupForm.Meta):
        widgets = {
            'zone': d_forms.HiddenInput(),
            'service_type': d_forms.HiddenInput()
        }


class EditNotesForm(d_forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = models.AllocationRequest
        fields = ('notes',)
