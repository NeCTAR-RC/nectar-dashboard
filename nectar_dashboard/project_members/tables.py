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

import logging

from django.conf import settings
from django.template import defaultfilters
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import tables
from openstack_dashboard import api

from nectar_dashboard.project_members import constants


LOG = logging.getLogger(__name__)


class UserFilterAction(tables.FilterAction):
    def filter(self, table, users, filter_string):
        """Naive case-insensitive search """
        q = filter_string.lower()
        return [user for user in users
                if q in user.name.lower()
                or q in user.email.lower()]


class RemoveMembers(tables.DeleteAction):
    name = "removeProjectMember"
    data_type_singular = _("User")
    data_type_plural = _("Users")

    def allowed(self, request, user=None):
        if not api.keystone.keystone_can_edit_project():
            return False
        if user:
            return user.id != request.user.id
        return True

    def action(self, request, obj_id):
        user_obj = self.table.get_object_by_id(obj_id)
        project_id = request.user.tenant_id
        LOG.info('Removing user %s from project %s.' % (user_obj.id,
                                                      project_id))
        role_id = getattr(settings, 'KEYSTONE_MEMBER_ROLE_ID', '1')
        api.keystone.remove_tenant_user_role(request,
                                             project=project_id,
                                             user=user_obj.id,
                                             role=role_id)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Remove Member",
            u"Remove Members",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Removed Member",
            u"Removed Members",
            count
        )


class AddMembersLink(tables.LinkAction):
    name = "add_user_link"
    verbose_name = _("Add...")
    classes = ("ajax-modal", "btn-create")
    url = constants.PROJECTS_ADD_MEMBER_URL

    def allowed(self, request, user=None):
        return api.keystone.keystone_can_edit_project()

    def get_link_url(self, datum=None):
        return reverse(self.url, kwargs=self.table.kwargs)


class UsersTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('User Name'),
                         filters=[defaultfilters.urlize])


class ProjectMembersTable(UsersTable):
    class Meta:
        name = "project_members"
        verbose_name = _("Project Users")
        table_actions = (UserFilterAction, AddMembersLink, RemoveMembers,)
        row_actions = (RemoveMembers,)
