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

from django.db.models import Q

from django.views.generic import detail

from horizon import tables as horizon_tables
from horizon import views

from nectar_dashboard.user_info import models

from . import forms
from . import tables


class UserListView(horizon_tables.DataTableView):
    """User search / lookup form + listing of users that match
    """

    table_class = tables.UsersTable
    template_name = "user_info/list.html"
    page_title = "User lookup"

    def get_data(self):
        email = self.request.GET.get('email')
        if email:
            return models.RCUser.objects.filter(Q(user_id__iexact=email)
                                                | Q(email__iexact=email))

        q = self.request.GET.get('q')
        if not q or len(q) < 3:
            return []
        return models.RCUser.objects.filter(Q(email__icontains=q)
                                            | Q(displayname__icontains=q))


class UserDetailView(views.PageTitleMixin, detail.DetailView):
    """A simple form for listing the user's details
    """
    model = models.RCUser
    form_class = forms.UserViewForm
    template_name = "user_info/view.html"
    page_title = "User Details"
