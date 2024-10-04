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

from django.urls import reverse
from django.urls import reverse_lazy
from horizon import exceptions
from horizon import forms

from nectar_dashboard.api import manuka
from nectar_dashboard.user_info.update import forms as user_forms


class UserEditSelfView(forms.ModalFormView):
    form_class = user_forms.UpdateForm
    modal_id = "update_user_modal"
    template_name = 'user_info/edit.html'
    submit_url = "horizon:settings:my-details:edit-self"
    success_url = reverse_lazy("horizon:settings:my-details:edit-self")
    page_title = "My Details"

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                keystone_user_id = self.request.user.keystone_user_id
                client = manuka.manukaclient(self.request)
                self._object = client.users.get(keystone_user_id)
            except Exception:
                msg = 'Unable to retrieve user.'
                url = reverse('horizon:settings')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_object()
        context['submit_url'] = reverse(self.submit_url)
        context['object'] = self.get_object()
        return context

    def get_initial(self):
        user = self.get_object()
        return user.to_dict()
