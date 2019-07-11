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

from django import forms

from nectar_dashboard.user_info import forms as base_forms

LOG = logging.getLogger(__name__)


class UserEditForm(base_forms.UserBaseForm):

    class Meta(base_forms.UserBaseForm.Meta):

        exclude = ['state', 'terms_accepted_at', 'registered_at',
                   'terms_version', 'shibboleth_attributes',
                   'ignore_username_not_email']
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['orcid'].required = False

    def clean(self):
        super().clean()
        # In the functional tests, something seems to be turning
        # None (DB NULL) values into 'None'.
        if self.cleaned_data['orcid'] == 'None':
            self.cleaned_data['orcid'] = None
        if self.cleaned_data['phone_number'] == 'None':
            self.cleaned_data['phone_number'] = None
        if self.cleaned_data['mobile_number'] == 'None':
            self.cleaned_data['mobile_number'] = None
