import datetime

from django import forms

from nectar_dashboard.rcallocation import forms as base_forms


class UserAllocationRequestForm(base_forms.AllocationRequestForm):
    next_status = 'E'

    class Meta(base_forms.AllocationRequestForm.Meta):
        exclude = ('project_id', 'status_explanation',) \
                  + base_forms.AllocationRequestForm.Meta.exclude

    def __init__(self, **kwargs):
        super(UserAllocationRequestForm, self).__init__(**kwargs)
        self.instance.status = self.next_status


class UserAllocationRequestAmendForm(base_forms.AllocationAmendRequestForm):
    next_status = 'X'

    class Meta(base_forms.AllocationAmendRequestForm.Meta):
        exclude = ('project_id', 'allocation_home',
                   'status_explanation', 'convert_project_trial'
                   ) + base_forms.AllocationAmendRequestForm.Meta.exclude

        widgets = {
            'project_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'project_description': forms.TextInput(
                attrs={'readonly': 'readonly'}),
            'contact_email': forms.TextInput(
                attrs={'readonly': 'readonly'}),
            'start_date': forms.TextInput(
                attrs={'class': 'datepicker col-md-12',
                       'style': 'border-radius:0;'}),
        }

    def __init__(self, **kwargs):
        initial = kwargs['initial']
        initial['start_date'] = datetime.date.today
        super(UserAllocationRequestAmendForm, self).__init__(**kwargs)
        self.instance.status = self.next_status
        self.fields['start_date'].label = 'Extension start date'
        self.fields['estimated_project_duration'].label = \
            'Estimated extension duration'
        self.initial['requested_allocation_home'] = \
            self.instance.allocation_home
