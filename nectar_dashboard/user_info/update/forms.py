import logging

from django import forms

from nectar_dashboard.user_info import forms as base_forms

LOG = logging.getLogger(__name__)


class UserEditForm(base_forms.UserBaseForm):

    class Meta(base_forms.UserBaseForm.Meta):
        widgets = {
            'persistent_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'user_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'displayname': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.TextInput(attrs={'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'surname': forms.TextInput(attrs={'readonly': 'readonly'}),
            'home_organization': forms.TextInput(
                attrs={'readonly': 'readonly'}),
            'orcid': forms.TextInput(),
            'phone_number': forms.TextInput(),
            'mobile_number': forms.TextInput(),
            'affiliation': forms.Select(),
        }
