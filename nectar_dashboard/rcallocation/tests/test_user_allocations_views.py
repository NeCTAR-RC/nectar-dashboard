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

from operator import itemgetter
from unittest import mock

from django.urls import reverse
from openstack_dashboard import api

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories


@mock.patch('nectar_dashboard.rcallocation.notifier.FreshdeskNotifier',
            new=base.FAKE_FD_NOTIFIER_CLASS)
class RequestTestCase(base.BaseTestCase):

    def assert_allocation(self, model, quotas=[], requestable=True,
                          institutions=[], publications=[],
                          grants=[], investigators=[],
                          **attributes):
        for field, value in attributes.items():
            if field not in ['quotas', 'institutions', 'publications',
                             'grants', 'investigators', 'usage_types']:
                self.assertEqual(getattr(model, field), value,
                                 "field that didn't match: %s" % field)
        self.assertEqual(list(attributes['usage_types']),
                         list(model.usage_types.all()))
        self.assertEqual(model.contact_email, self.user.name)
        # Sort by requested quota so we can easily compare by iterating
        # (Note that this is a bit dodgy since the requested quotas are
        # typically fuzzed ... and there is a small probability that two
        # different quota values will be the same.)
        kwargs = {'group__allocation': model}
        if requestable:
            kwargs['resource__requestable'] = True
        quotas_l = models.Quota.objects.filter(**kwargs) \
                   .order_by('requested_quota')
        quotas = sorted(quotas, key=itemgetter('requested_quota'))
        self.assertEqual(quotas_l.count(), len(quotas))
        for i, quota_model in enumerate(quotas_l):
            self.assertEqual(quota_model.resource.id, quotas[i]['resource'])
            self.assertEqual(quota_model.group.zone.name, quotas[i]['zone'])
            self.assertEqual(quota_model.requested_quota,
                             quotas[i]['requested_quota'])
            self.assertEqual(quota_model.quota, quotas[i]['quota'])

        institutions_l = model.institutions.all()
        for i, institution_model in enumerate(institutions_l):
            self.assertEqual(institution_model.name, institutions[i]['name'])

        publications_l = model.publications.all()
        for i, pub_model in enumerate(publications_l):
            self.assertEqual(pub_model.publication,
                             publications[i]['publication'])

        grants_l = model.grants.all()
        for i, grant_model in enumerate(grants_l):
            self.assertEqual(grant_model.grant_type, grants[i]['grant_type'])

        investigators_l = model.investigators.all()
        for i, investigator_model in enumerate(investigators_l):
            self.assertEqual(investigator_model.email,
                             investigators[i]['email'])

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

    @mock.patch.object(api.nova, 'tenant_absolute_limits')
    def test_edit_allocation_request(self, mock_nova_limits):

        mock_nova_limits.return_value = {}

        allocation = factories.AllocationFactory.create(
            contact_email=self.user.name)
        initial_state = common.allocation_to_dict(
            models.AllocationRequest.objects.get(pk=allocation.pk))
        initial_mod = allocation.modified_time

        response = self.client.get(
            reverse('horizon:allocation:user_requests:edit_request',
                    args=(allocation.id,)))
        self.assertStatusCode(response, 200)
        expected_model, form = common.request_allocation(user=self.user,
                                                         model=allocation)

        form['ignore_warnings'] = True

        response = self.client.post(
            reverse('horizon:allocation:user_requests:edit_request',
                    args=(allocation.id,)),
            form)

        # Check to make sure we were redirected back to the index of
        # our requests.
        self.assertStatusCode(response, 302)
        self.assertEqual('../../', response.get('location'))

        model = (models.AllocationRequest.objects.get(
            project_description=form['project_description'],
            parent_request_id=None))

        self.assert_allocation(model, status='E', **expected_model)
        self.assert_history(model, initial_state, initial_mod)

    @mock.patch.object(api.nova, 'tenant_absolute_limits')
    def test_amend_allocation_request(self, mock_nova_limits):

        mock_nova_limits.return_value = {}

        allocation = factories.AllocationFactory.create(
            contact_email=self.user.name, status='A')
        initial_state = common.allocation_to_dict(
            models.AllocationRequest.objects.get(pk=allocation.pk))
        initial_mod = allocation.modified_time

        response = self.client.get(
            reverse('horizon:allocation:user_requests:edit_change_request',
                    args=(allocation.id,)))
        self.assertStatusCode(response, 200)
        expected_model, form = common.request_allocation(user=self.user,
                                                         model=allocation)

        form['ignore_warnings'] = True

        response = self.client.post(
            reverse('horizon:allocation:user_requests:edit_change_request',
                    args=(allocation.id,)),
            form)

        # Check to make sure we were redirected back to the index of
        # our requests.
        self.assertStatusCode(response, 302)
        self.assertEqual('../../', response.get('location'))

        model = (models.AllocationRequest.objects.get(
            project_description=form['project_description'],
            parent_request_id=None))

        self.assert_allocation(model, status='X', **expected_model)
        self.assert_history(model, initial_state, initial_mod)
