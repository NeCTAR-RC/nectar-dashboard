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

from openstack_dashboard.test import helpers
from rest_framework import test

from keystoneclient.v3 import roles

from nectar_dashboard.rcallocation import models

from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories
from nectar_dashboard.rcallocation.tests import utils


FAKE_FD_NOTIFIER = mock.MagicMock()
FAKE_FD_NOTIFIER.__enter__.return_value = FAKE_FD_NOTIFIER
FAKE_FD_NOTIFIER_CLASS = mock.MagicMock(return_value=FAKE_FD_NOTIFIER)


class BaseTestCase(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.sites_setup()
        common.approvers_setup()
        common.factory_setup()


class BaseApproverTestCase(helpers.BaseAdminViewTests):
    """Sets an active user with the "AllocationAdmin" role.

    For testing approver-only views and functionality.
    """

    def setUp(self):
        super().setUp()
        common.sites_setup()
        common.approvers_setup()
        common.factory_setup()

    def setActiveUser(self, *args, **kwargs):
        if "roles" not in kwargs:
            allocation_admin_role_dict = {'id': '142',
                                          'name': 'allocationadmin'}
            allocation_admin_role = roles.Role(roles.RoleManager,
                                               allocation_admin_role_dict,
                                               loaded=True)
            self.roles.add(allocation_admin_role)
            self.roles.allocation_admin = allocation_admin_role
            kwargs['roles'] = [self.roles.allocation_admin._info]
            super().setActiveUser(*args, **kwargs)


class AllocationAPITest(test.APITestCase):

    def setUp(self, *args, **kwargs):
        common.sites_setup()
        common.factory_setup()
        common.usage_types_setup()
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
            contact_email=self.user.username,
            status=models.AllocationRequest.SUBMITTED,
            create_quotas=False)
