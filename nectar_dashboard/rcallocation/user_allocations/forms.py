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
        fields = ['project_name', 'project_description', 'contact_email',
                  'estimated_project_duration', 'use_case', 'usage_patterns',
                  'geographic_requirements', 'estimated_number_users',
                  'field_of_research_1', 'for_percentage_1',
                  'field_of_research_2', 'for_percentage_2',
                  'field_of_research_3', 'for_percentage_3',
                  'ardc_support', 'ardc_explanation',
                  'ncris_explanation', 'ncris_facilities',
                  'usage_types', 'supported_organisations',
                  'bundle', 'ignore_warnings']

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
