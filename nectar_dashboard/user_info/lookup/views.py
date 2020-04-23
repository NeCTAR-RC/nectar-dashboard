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

from horizon import exceptions
from horizon import tables
from horizon import views

from nectar_dashboard.api import manuka

from . import tables as user_tables


class UserListView(tables.PagedTableMixin, tables.DataTableView):
    table_class = user_tables.UsersTable
    page_title = "User Search"
    template_name = "user_info/list.html"

    def get_data(self):
        q = self.request.GET.get('q')
        if not q or len(q) < 3:
            return []
        try:
            client = manuka.manukaclient(self.request)
            return client.users.search(q)
        except Exception:
            exceptions.handle(self.request,
                              'Unable to search users.')
            return []


class UserDetailView(views.HorizonTemplateView):
    template_name = "user_info/view.html"
    page_title = "User Details"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_data()
        context["object"] = user
        return context

    def get_data(self):
        try:
            user_id = self.kwargs['user_id']
            client = manuka.manukaclient(self.request)
            user = client.users.get(user_id)
        except Exception:
            exceptions.handle(self.request,
                              'Unable to retrieve user details.')
        return user
