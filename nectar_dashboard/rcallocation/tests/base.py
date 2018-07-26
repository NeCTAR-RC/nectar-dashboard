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

from rest_framework import test

from nectar_dashboard.rcallocation.tests import factories
from nectar_dashboard.rcallocation.tests import utils


class AllocationAPITest(test.APITestCase):

    def setUp(self, *args, **kwargs):
        self.user = utils.get_user(id='user1',
                                   username='bob',
                                   project_name='proj1')
        self.user2 = utils.get_user(id='user2',
                                    username='fred',
                                    project_name='proj2')
        self.approver_user = utils.get_user(id='approver',
                                            username='approver',
                                            project_name='proj3',
                                            roles=['tenantmanager'])
        self.admin_user = utils.get_user(id='admin',
                                         username='admin',
                                         project_name='admin-proj',
                                         roles=['admin'])
        self.allocation = factories.AllocationFactory.create(
            contact_email=self.user.username, status='E', create_quotas=False)
