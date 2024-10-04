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


from horizon.utils import memoized
from keystoneauth1 import session
from langstrothclient import client
from openstack_auth import utils

LANGSTROTH_API_VERSION = '1'


@memoized.memoized
def langstrothclient(request):
    unscoped_token = request.user.unscoped_token
    endpoint = request.user.endpoint
    tenant_id = request.user.tenant_id
    auth = utils.get_token_auth_plugin(
        auth_url=endpoint, token=unscoped_token, project_id=tenant_id
    )

    keystone_session = session.Session(auth=auth)

    return client.Client(LANGSTROTH_API_VERSION, session=keystone_session)
