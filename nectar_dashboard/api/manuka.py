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
from keystoneauth1.identity import v3
from keystoneauth1 import session
from manukaclient import client


MANUKA_API_VERSION = '1'


@memoized.memoized
def manukaclient(request):
    auth = v3.Token(token=request.user.token.id,
                    project_id=request.user.tenant_id,
                    auth_url=request.user.endpoint)

    keystone_session = session.Session(auth=auth)

    return client.Client(MANUKA_API_VERSION, session=keystone_session)
