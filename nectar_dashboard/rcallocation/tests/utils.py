#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from unittest import mock

from django.conf import settings

from openstack_auth import user


def get_user(id='123', username='bob', project_name='foo', roles=['member']):
    roles = [{'name': role} for role in roles]
    project_id = 'id' + project_name
    project = {'id': project_id}
    token = mock.Mock(project=project, tenant=project)
    return user.User(
        id=id,
        token=token,
        user=username,
        domain_id='default',
        user_domain_name='Default',
        tenant_id=project_id,
        tenant_name=project_name,
        service_catalog={},
        roles=roles,
        enabled=True,
        authorized_tenants=[project_name],
        endpoint=settings.OPENSTACK_KEYSTONE_URL,
    )
