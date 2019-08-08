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
