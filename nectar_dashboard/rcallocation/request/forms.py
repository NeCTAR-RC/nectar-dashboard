from nectar_dashboard.rcallocation import forms as base_forms


class UserAllocationRequestForm(base_forms.AllocationRequestForm):
    class Meta(base_forms.AllocationRequestForm.Meta):
        exclude = (
            'status_explanation',
        ) + base_forms.AllocationRequestForm.Meta.exclude
