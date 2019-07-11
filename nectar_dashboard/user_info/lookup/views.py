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
        q = self.request.GET.get('q')
        verb = self.request.GET.get('verb')
        if not q or len(q) < 3:
            return []

        if verb == 'lookup':
            return models.RCUser.objects.filter(Q(user_id__iexact=q)
                                                | Q(email__iexact=q))
        elif verb == 'search':
            return models.RCUser.objects.filter(Q(email__icontains=q)
                                                | Q(displayname__icontains=q))
        else:
            return []


class UserDetailView(views.PageTitleMixin, detail.DetailView):
    """A simple form for listing the user's details
    """
    model = models.RCUser
    form_class = forms.UserViewForm
    template_name = "user_info/view.html"
    page_title = "User Details"
