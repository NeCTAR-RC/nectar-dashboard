# vim: tabstop=4 shiftwidth=4 softtabstop=4

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
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard import api

from nectar_dashboard.project_members import api as api_ext


LOG = logging.getLogger(__name__)


class AddUserToProjectForm(forms.SelfHandlingForm):
    email = forms.EmailField(label=mark_safe("Username"), required=True)

    def handle(self, request, data):
        project_id = request.user.tenant_id
        role_id = getattr(settings, 'KEYSTONE_MEMBER_ROLE_ID', '1')

        try:
            email = data['email']
            user = api_ext.user_get_by_name(request, email)
            api.keystone.add_tenant_user_role(
                request, project=project_id, user=user.id, role=role_id
            )
            messages.success(request, _('User added successfully.'))
        except api_ext.UserNotFound:
            exceptions.handle(
                request,
                'Unable to add user to project: there is no '
                f'Nectar RC account registered for "{email}"',
            )
            return False
        except Exception as e:
            LOG.exception(e)
            exceptions.handle(request, 'Unable to add user to project.')
            return False
        return True
