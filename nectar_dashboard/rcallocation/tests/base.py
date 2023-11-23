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
        common.factory_setup()
        self.maxDiff = None

    def assert_allocation(self, model, quotas=[], supported_organisations=[],
                          publications=[], grants=[], investigators=[],
                          usage_types=[], **attributes):
        """Check that 'model' AllocationRequest and its dependents
        match the expected state as given by the keyword args.
        """

        for field, value in attributes.items():
            self.assertEqual(getattr(model, field), value,
                             "field that didn't match: %s" % field)
        self.assertEqual(set(usage_types), set(model.usage_types.all()))
        self.assertEqual(model.contact_email, self.user.name)

        self.assertEqual(set(model.supported_organisations.all()),
                         set(supported_organisations))

        quotas_l = models.Quota.objects.filter(group__allocation=model)
        # (For ... reasons ... there may be zero-valued quotas in the list)
        quotas = [q for q in quotas if q['quota'] > 0
                  or q['requested_quota'] > 0]

        # For debugging purposes ....
        if quotas_l.count() != len(quotas):
            print(f"expected quotas - {quotas}")
            print("actual quotas")
            for qm in quotas_l:
                print(f"resource {qm.resource.id}, "
                      f"({qm.resource.quota_name}), "
                      f"zone {qm.group.zone.name},"
                      f"requested quota {qm.requested_quota}, "
                      f"quota {qm.quota}")

        self.assertEqual(quotas_l.count(), len(quotas))
        # (The order of the quotas don't need to match ...)
        for qm in quotas_l:
            matched = [q for q in quotas if q['resource'] == qm.resource.id
                       and q['zone'] == qm.group.zone.name]
            self.assertEqual(len(matched), 1)
            self.assertEqual(qm.group.zone.name, matched[0]['zone'])
            self.assertEqual(qm.requested_quota,
                             matched[0]['requested_quota'])
            self.assertEqual(qm.quota, matched[0]['quota'])

        publications_l = model.publications.all()
        for i, pub_model in enumerate(publications_l):
            self.assertEqual(pub_model.publication,
                             publications[i]['publication'])

        grants_l = model.grants.all()
        for i, g_model in enumerate(grants_l):
            self.assertEqual(g_model.grant_type, grants[i]['grant_type'])
            self.assertEqual(g_model.funding_body_scheme, grants[i][
                'funding_body_scheme'])
            self.assertEqual(g_model.grant_id, grants[i]['grant_id'])
            self.assertEqual(g_model.first_year_funded,
                             grants[i]['first_year_funded'])
            self.assertEqual(g_model.last_year_funded,
                             grants[i]['last_year_funded'])
            self.assertEqual(g_model.total_funding, grants[i]['total_funding'])

        investigators_l = model.investigators.all()
        for i, inv_m in enumerate(investigators_l):
            self.assertEqual(inv_m.title, investigators[i]['title'])
            self.assertEqual(inv_m.given_name, investigators[i]['given_name'])
            self.assertEqual(inv_m.surname, investigators[i]['surname'])
            self.assertEqual(inv_m.email, investigators[i]['email'])
            self.assertEqual(inv_m.additional_researchers, investigators[i][
                'additional_researchers'])

    def assert_history(self, model, initial_state, initial_mod):
        # check historical allocation model
        old_model = (models.AllocationRequest.objects.get(
            parent_request_id=model.id))
        old_state = common.allocation_to_dict(old_model)

        # check modification dates
        self.assertEqual(initial_mod, old_model.modified_time)
        self.assertTrue(initial_mod < model.modified_time)

        # some fields are changed during the archive process, these
        # fields should not be compared.
        for invalid_field in ['id', 'parent_request']:
            del old_state[invalid_field]
            del initial_state[invalid_field]

        self.assertEqual(old_state, initial_state,
                         msg="allocation fields changed unexpectedly")


class BaseApproverTestCase(helpers.BaseAdminViewTests):
    """Sets an active user with the "AllocationAdmin" role.

    For testing approver-only views and functionality.
    """

    def setUp(self):
        super().setUp()
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
        common.factory_setup()
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
