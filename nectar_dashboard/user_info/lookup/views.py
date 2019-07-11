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

from django.core.urlresolvers import reverse
from django.db.models import Q

from django.views.generic import detail
from django.views.generic import edit

from horizon import tables as horizon_tables

from nectar_dashboard.user_info import models
from nectar_dashboard.user_info import views

from . import forms
from . import tables


class UserLookupView(views.PageTitleMixin, edit.FormView):
    """A simple form view for user lookup
    """

    form_class = forms.UserLookupForm
    template_name = "user_info/lookup.html"
    page_title = "User Info Lookup"

    def form_valid(self, form):
        self.form = form
        return super(UserLookupView, self).form_valid(form)

    def get_success_url(self):
        email = self.form.cleaned_data['email']
        return reverse('horizon:identity:lookup:list',
                       kwargs={'email': email})


class UserListView(views.PageTitleMixin, horizon_tables.DataTableView):
    """A simple listing of users matching a lookup
    """

    table_class = tables.UsersTable
    template_name = "user_info/list.html"
    page_title = "Matching Users"

    def get_data(self):
        email = self.kwargs['email']
        return models.User.objects.filter(Q(user_id__iexact=email)
                                          | Q(email__iexact=email))


class UserDetailView(views.PageTitleMixin, detail.DetailView,
                     edit.ModelFormMixin):
    """A simple form for listing the user's details
    """
    model = models.User
    form_class = forms.UserViewForm
    template_name = "user_info/view.html"
    page_title = "User Info"

    def get(self, *args, **kwargs):
        res = super(detail.DetailView, self).get(*args, **kwargs)
        return res
