import logging

from django import forms

from nectar_dashboard.user_info import models

LOG = logging.getLogger(__name__)


class UserBaseForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = '__all__'

    def __init(self):
        super(UserBaseForm, self).__init()
        for name, field in self.fields.items():
            if 'readonly' in field.widget.attrs:
                field.disabled = True


class UserEditForm(UserBaseForm):
    pass


class UserViewForm(UserBaseForm):

    class Meta(UserBaseForm.Meta):
        widgets = {
            'persistent_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'user_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'displayname': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def is_valid(self):
        # Just in case ...
        return False
