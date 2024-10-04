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

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories


@mock.patch(
    'nectar_dashboard.rcallocation.notifier.FreshdeskNotifier',
    new=base.FAKE_FD_NOTIFIER_CLASS,
)
class RequestTestCase(base.BaseTestCase):
    def test_edit_allocation_request(self):
        allocation = factories.AllocationFactory.create(
            contact_email=self.user.name
        )
        initial_state = common.allocation_to_dict(
            models.AllocationRequest.objects.get(pk=allocation.pk)
        )
        initial_mod = allocation.modified_time

        response = self.client.get(
            reverse(
                'horizon:allocation:user_requests:edit_request',
                args=(allocation.id,),
            )
        )
        self.assertStatusCode(response, 200)
        expected_model, form = common.request_allocation(
            user=self.user, model=allocation
        )

        # Update the use case in this edit
        expected_model['use_case'] = form['use_case'] = 'new use case'
        form['ignore_warnings'] = True

        response = self.client.post(
            reverse(
                'horizon:allocation:user_requests:edit_request',
                args=(allocation.id,),
            ),
            form,
        )

        # Check to make sure we were redirected back to the index of
        # our requests.
        self.assertStatusCode(response, 302)
        self.assertEqual('../../', response.get('location'))

        model = models.AllocationRequest.objects.get(
            project_description=form['project_description'],
            parent_request_id=None,
        )

        self.assert_allocation(model, status='E', **expected_model)
        self.assert_history(model, initial_state, initial_mod)

    def test_amend_allocation_request(self):
        allocation = factories.AllocationFactory.create(
            contact_email=self.user.name, status='A'
        )

        # For an approved allocation we init the form with
        # approved quotas as opposed to requested quotas
        # So we should "approve" all the requested quotas
        # first.
        for quota in models.Quota.objects.filter(group__allocation=allocation):
            quota.quota = quota.requested_quota
            quota.save()
        initial_state = common.allocation_to_dict(
            models.AllocationRequest.objects.get(pk=allocation.pk)
        )
        initial_mod = allocation.modified_time

        response = self.client.get(
            reverse(
                'horizon:allocation:user_requests:edit_change_request',
                args=(allocation.id,),
            )
        )
        self.assertStatusCode(response, 200)
        expected_model, form = common.request_allocation(
            user=self.user, model=allocation, amending=True
        )
        # Update the use case in this edit
        expected_model['use_case'] = form['use_case'] = 'new use case'
        form['ignore_warnings'] = True

        response = self.client.post(
            reverse(
                'horizon:allocation:user_requests:edit_change_request',
                args=(allocation.id,),
            ),
            form,
        )

        # Check to make sure we were redirected back to the index of
        # our requests.
        self.assertStatusCode(response, 302)
        self.assertEqual('../../', response.get('location'))

        model = models.AllocationRequest.objects.get(
            project_description=form['project_description'],
            parent_request_id=None,
        )
        self.assert_allocation(model, status='X', **expected_model)
        self.assert_history(model, initial_state, initial_mod)

    def test_edit_allocation_request_convert_to_bundle(self):
        allocation = factories.AllocationFactory.create(
            contact_email=self.user.name
        )
        initial_state = common.allocation_to_dict(
            models.AllocationRequest.objects.get(pk=allocation.pk)
        )
        initial_mod = allocation.modified_time

        response = self.client.get(
            reverse(
                'horizon:allocation:user_requests:edit_request',
                args=(allocation.id,),
            )
        )
        self.assertStatusCode(response, 200)
        gold = models.Bundle.objects.get(name='gold')
        expected_model, form = common.request_allocation(
            user=self.user, model=allocation, bundle=gold
        )

        form['ignore_warnings'] = True

        response = self.client.post(
            reverse(
                'horizon:allocation:user_requests:edit_request',
                args=(allocation.id,),
            ),
            form,
        )

        # Check to make sure we were redirected back to the index of
        # our requests.
        self.assertStatusCode(response, 302)
        self.assertEqual('../../', response.get('location'))

        model = models.AllocationRequest.objects.get(
            project_description=form['project_description'],
            parent_request_id=None,
        )

        self.assert_allocation(model, status='E', **expected_model)
        self.assert_history(model, initial_state, initial_mod)

    def test_edit_allocation_request_convert_from_bundle(self):
        silver = models.Bundle.objects.get(name='silver')

        allocation = factories.AllocationFactory.create(
            contact_email=self.user.name, bundle=silver, create_quotas=False
        )
        melbourne = models.Zone.objects.get(name='melbourne')
        volume_st = models.ServiceType.objects.get(catalog_name='volume')
        volumes = models.Resource.objects.get(
            quota_name='gigabytes', service_type=volume_st
        )
        group_volume_melbourne = factories.QuotaGroupFactory(
            allocation=allocation, service_type=volume_st, zone=melbourne
        )
        factories.QuotaFactory(group=group_volume_melbourne, resource=volumes)

        initial_state = common.allocation_to_dict(
            models.AllocationRequest.objects.get(pk=allocation.pk)
        )
        initial_mod = allocation.modified_time

        response = self.client.get(
            reverse(
                'horizon:allocation:user_requests:edit_request',
                args=(allocation.id,),
            )
        )
        self.assertStatusCode(response, 200)

        expected_model, form = common.request_allocation(
            user=self.user, model=allocation
        )

        form['ignore_warnings'] = True

        response = self.client.post(
            reverse(
                'horizon:allocation:user_requests:edit_request',
                args=(allocation.id,),
            ),
            form,
        )

        # Check to make sure we were redirected back to the index of
        # our requests.
        self.assertStatusCode(response, 302)
        self.assertEqual('../../', response.get('location'))

        model = models.AllocationRequest.objects.get(
            project_description=form['project_description'],
            parent_request_id=None,
        )

        self.assert_allocation(model, status='E', **expected_model)
        self.assert_history(model, initial_state, initial_mod)
