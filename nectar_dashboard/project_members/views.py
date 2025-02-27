# Copyright 2013 Hewlett-Packard Development Company, L.P.
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
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tables
from openstack_dashboard import api

from nectar_dashboard.project_members import constants
from nectar_dashboard.project_members.forms import AddUserToProjectForm
from nectar_dashboard.project_members.tables import ProjectMembersTable


class User:
    def __init__(self, user_dict, role_dict):
        for k, v in user_dict.items():
            setattr(self, k, v)
        self.role_name = role_dict.get('name')
        self.role_id = role_dict.get('id')
        # We need unique ids so combo of user id and role id.
        # Store user id in different field so to use in remove stage
        # in tables.py
        self.user_id = self.id
        self.id = f"{self.id}-{self.role_id}"


class ProjectManageMixin:
    def _get_project(self):
        if not hasattr(self, "_project"):
            tenant_id = self.request.user.tenant_id
            self._project = api.keystone.tenant_get(self.request, tenant_id)
        return self._project

    def _get_project_members(self):
        if not hasattr(self, "_project_members"):
            tenant_id = self.request.user.tenant_id
            project_members = []
            assignments = api.keystone.role_assignments_list(
                self.request,
                project=tenant_id,
                include_subtree=False,
                include_names=True,
            )

            for a in assignments:
                if a.role.get('name').lower() in ['member', 'tenantmanager']:
                    project_members.append(User(a.user, a.role))
            self._project_members = project_members

        return self._project_members

    def _get_project_non_members(self):
        return []


class ManageMembersView(ProjectManageMixin, tables.DataTableView):
    table_class = ProjectMembersTable
    template_name = constants.PROJECTS_INDEX_VIEW_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self._get_project()
        return context

    def get_data(self):
        project_members = []
        try:
            project_members = self._get_project_members()
        except Exception:
            exceptions.handle(
                self.request, _('Unable to retrieve project users.')
            )
        return project_members


class AddUserToProjectView(forms.ModalFormView):
    form_class = AddUserToProjectForm
    template_name = constants.PROJECTS_ADD_MEMBER_VIEW_TEMPLATE
    ajax_template_name = constants.PROJECTS_ADD_MEMBER_AJAX_VIEW_TEMPLATE

    def get_success_url(self):
        return reverse(constants.PROJECTS_INDEX_URL)
