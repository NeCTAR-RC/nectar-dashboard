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

from django.core.urlresolvers import reverse

import mock

from nectar_dashboard.rcallocation import models

from openstack_dashboard import api
from openstack_dashboard.test.helpers import TestCase

from .factories import AllocationFactory
from .common import allocation_to_dict, request_allocation


class RequestTestCase(TestCase):

    def assert_allocation(self, model, quotas=[],
                          institutions=[], publications=[],
                          grants=[], investigators=[], **attributes):
        for field, value in attributes.items():
            assert getattr(model, field) == value
        self.assertEqual(model.contact_email, self.user.name)
        # Sort by requested quota so we can easily compare by iterating
        quotas_l = models.Quota.objects.filter(
            group__allocation=model).order_by('requested_quota')
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
            assert institution_model.name == institutions[i]['name']

        publications_l = model.publications.all()
        for i, pub_model in enumerate(publications_l):
            assert pub_model.publication == publications[i]['publication']

        grants_l = model.grants.all()
        for i, grant_model in enumerate(grants_l):
            assert grant_model.grant_type == grants[i]['grant_type']

        investigators_l = model.investigators.all()
        for i, investigator_model in enumerate(investigators_l):
            assert investigator_model.email == investigators[i]['email']

    @mock.patch.object(api.nova, 'tenant_absolute_limits')
    def test_edit_allocation_request(self, mock_nova_limits):

        mock_nova_limits.return_value = {}

        allocation = AllocationFactory.create(contact_email=self.user.name)
        initial_state = allocation_to_dict(
            models.AllocationRequest.objects.get(pk=allocation.pk))

        response = self.client.get(
            reverse('horizon:allocation:user_requests:edit_request',
                    args=(allocation.id,)))
        self.assertStatusCode(response, 200)
        expected_model, form = request_allocation(user=self.user,
                                                  model=allocation)

        # Tells the server to skip the sanity checks.  (For these to work in
        # this test, the request needs to be populated with sane quotas for
        # resources that mirror those understood by the sanity check code.
        # The sanity checks will be tested another way.)
        form['ignore_warnings'] = True

        response = self.client.post(
            reverse('horizon:allocation:user_requests:edit_request',
                    args=(allocation.id,)),
            form)

        # Check to make sure we were redirected back to the index of
        # our requests.
        self.assertStatusCode(response, 302)
        self.assertEqual(
            'http://testserver' +
            reverse('horizon:allocation:user_requests:index'),
            response.get('location'))
        model = (models.AllocationRequest.objects.get(
            project_description=form['project_description'],
            parent_request_id=None))

        self.assert_allocation(model, **expected_model)

        # check historical allocation model
        old_model = (models.AllocationRequest.objects.get(
            parent_request_id=model.id))
        old_state = allocation_to_dict(old_model)

        # some fields are changed during the archive process, these
        # fields should not be compared.
        for invalid_field in ['modified_time', 'id', 'parent_request']:
            del old_state[invalid_field]
            del initial_state[invalid_field]

        for quota in old_state['quota'] + initial_state['quota']:
            del quota['id']
            del quota['allocation']

        assert old_state == initial_state
