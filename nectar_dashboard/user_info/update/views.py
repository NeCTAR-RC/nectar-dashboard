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

from django.urls import reverse_lazy
from django.views.generic import edit

from horizon import views

from nectar_dashboard.user_info import models

from . import forms


class UserEditSelfView(views.PageTitleMixin, edit.UpdateView):
    """A simple form view for editing the user's own details
    """
    model = models.RCUser
    form_class = forms.UserEditForm
    template_name = "user_info/edit.html"
    page_title = "My Details"
    success_url = reverse_lazy('horizon:settings:update:edit-self')

    def get_object(self):
        user_id = self.request.user.keystone_user_id
        return models.RCUser.objects.filter(user_id=user_id) \
            .order_by('-last_login').first()
