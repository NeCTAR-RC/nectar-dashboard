# Copyright 2019 Australian Research Data Commons
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.db.models import Q
from django import forms
from django.utils.safestring import mark_safe

from nectar_dashboard.user_info import forms as base_forms
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


class UserViewForm(base_forms.UserBaseForm):

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
            'orcid': forms.TextInput(attrs={'readonly': 'readonly'}),
            'phone_number': forms.TextInput(attrs={'readonly': 'readonly'}),
            'mobile_number': forms.TextInput(attrs={'readonly': 'readonly'}),
            'affiliation': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def is_valid(self):
        # Just in case ...
        return False
