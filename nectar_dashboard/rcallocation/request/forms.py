from nectar_dashboard.rcallocation import forms


class UserAllocationRequestForm(forms.AllocationRequestForm):
    class Meta(forms.AllocationRequestForm.Meta):
        exclude = ('status_explanation',
                   ) + forms.AllocationRequestForm.Meta.exclude
