import logging

from django.db.models import Q
from django import forms
from django.utils.safestring import mark_safe

from nectar_dashboard.user_info import models

LOG = logging.getLogger(__name__)


class UserLookupForm(forms.Form):
    email = forms.EmailField(label=mark_safe("Account or email address"),
                             required=True)

    def is_valid(self):
        if not super(UserLookupForm, self).is_valid():
            return False
        form_email = self.cleaned_data['email']
        users = models.User.objects.filter(Q(user_id__iexact=form_email)
                                           | Q(email__iexact=form_email))
        if len(users) > 0:
            return True
        else:
            self.add_error('email', 'No users match this identifier')
            return False
