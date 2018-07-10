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

from django.conf import settings
from django.conf.urls import url
from django.conf.urls import include

from rest_framework.test import APITestCase

from nectar_dashboard.rcallocation.tests import factories
from nectar_dashboard.rcallocation.tests import utils


class AllocationAPITest(APITestCase):

    def setUp(self, *args, **kwargs):
        self.user = utils.get_user()
        self.user2 = utils.get_user(id='user2')
        self.approver_user = utils.get_user(id='approver', roles=['tenantmanager'])
        self.admin_user = utils.get_user(id='admin', roles=['admin'])
        self.allocation = factories.AllocationFactory.create(
            created_by=self.user.id, status='E', create_quotas=False)
