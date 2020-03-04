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
