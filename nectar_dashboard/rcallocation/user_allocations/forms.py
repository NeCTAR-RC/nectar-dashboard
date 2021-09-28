from django import forms

from nectar_dashboard.rcallocation import forms as base_forms


class UserAllocationRequestForm(base_forms.AllocationRequestForm):
    next_status = 'E'

    class Meta(base_forms.AllocationRequestForm.Meta):
        exclude = ('project_id', 'status_explanation',) \
                  + base_forms.AllocationRequestForm.Meta.exclude

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.instance.status = self.next_status


class UserAllocationRequestAmendForm(base_forms.AllocationAmendRequestForm):
    next_status = 'X'

    class Meta(base_forms.AllocationAmendRequestForm.Meta):
        exclude = ('project_id', 'allocation_home',
                   'associated_site', 'special_approval', 'national',
                   'status_explanation', 'convert_project_trial'
                   ) + base_forms.AllocationAmendRequestForm.Meta.exclude

        widgets = {
            'project_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'project_description': forms.TextInput(
                attrs={'readonly': 'readonly'}),
            'contact_email': forms.TextInput(
                attrs={'readonly': 'readonly'}),
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.instance.status = self.next_status
        self.fields['estimated_project_duration'].label = \
            'Estimated extension duration'
