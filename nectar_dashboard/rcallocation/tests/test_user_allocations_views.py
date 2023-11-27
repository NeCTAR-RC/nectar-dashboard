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

from django.urls import reverse
from openstack_dashboard import api

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories


@mock.patch('nectar_dashboard.rcallocation.notifier.FreshdeskNotifier',
            new=base.FAKE_FD_NOTIFIER_CLASS)
class RequestTestCase(base.BaseTestCase):

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

        # For an approved allocaton we init the form with
        # approved quotas as opposed to requested quotas
        # So we should "approve" all the requested quotas
        # first.
        for quota in models.Quota.objects.filter(group__allocation=allocation):
            quota.quota = quota.requested_quota
            quota.save()
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
