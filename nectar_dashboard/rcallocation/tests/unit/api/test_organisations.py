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

from rest_framework import exceptions
from rest_framework import status

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories


@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class OrganisationTest(base.AllocationAPITest):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.admin_approver = models.Approver.objects.create(
            username=self.admin_user.username,
            display_name="Fred the Admin")

    def _make_data(self,
                   full_name='University of Testing Australia',
                   short_name='UTA', country='AU',
                   **kwargs):
        data = {'full_name': full_name,
                'short_name': short_name,
                'country': country
        }
        data.update(kwargs)
        return data

    def _check_data(self, expected, actual, extra={}):
        e = {'enabled': True, 'ror_id': '', 'parent': None, 'precedes': []}
        e.update(expected)
        e.update(extra)
        d = actual.copy()
        for k in ['id', 'proposed_by', 'vetted_by']:
            d.pop(k, None)
            e.pop(k, None)
        self.assertCountEqual(e, d)

    def test_list(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/rest_api/organisations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

    def test_list_as_approver(self):
        self.client.force_authenticate(user=self.approver_user)
        response = self.client.get('/rest_api/organisations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

    def test_list_as_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/organisations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

    def test_list_anon(self):
        response = self.client.get('/rest_api/organisations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest_api/organisations/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('QCIF', response.data['short_name'])
        self.assertNotIn('vetted_by', response.data.keys())
        self.assertNotIn('proposed_by', response.data.keys())

    def test_get_as_approver(self):
        self.client.force_authenticate(user=self.approver_user)
        response = self.client.get('/rest_api/organisations/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('QCIF', response.data['short_name'])
        self.assertEqual(None, response.data['vetted_by'])
        self.assertEqual('', response.data['proposed_by'])

    def test_approve_anon(self):
        response = self.client.post('/rest_api/organisations/1/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_as_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest_api/organisations/1/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        org = factories.OrganisationFactory.create(proposed_by="someone")
        response = self.client.post(
            f'/rest_api/organisations/{org.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['enabled'])
        self.assertEqual(self.admin_approver.pk, response.data['vetted_by'])
        self.assertEqual("someone", response.data['proposed_by'])

    def test_approve_as_admin_bad(self):
        self.client.force_authenticate(user=self.admin_user)
        org = factories.OrganisationFactory.create(ror_id="https://xyz")
        response = self.client.post(
            f'/rest_api/organisations/{org.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_as_admin_unknown(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/rest_api/organisations/99/approve/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decline_anon(self):
        response = self.client.post('/rest_api/organisations/1/decline/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_decline_as_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest_api/organisations/1/decline/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_decline_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        org = factories.OrganisationFactory.create(proposed_by="someone")
        response = self.client.post(
            f'/rest_api/organisations/{org.id}/decline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['enabled'])
        self.assertEqual(self.admin_approver.pk, response.data['vetted_by'])
        self.assertEqual("someone", response.data['proposed_by'])

    def test_create_anon(self):
        response = self.client.post('/rest_api/organisations/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = self._make_data(url="https://www.uta.edu.au",
                               ror_id="https://ror.org/spqr01")
        response = self.client.post('/rest_api/organisations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._check_data(data, response.data, extra={'enabled': False})
        org = models.Organisation.objects.get(pk=response.data['id'])
        self.assertFalse(org.proposed_by)
        self.assertIsNone(org.vetted_by)

    def test_propose_as_user(self):
        self.client.force_authenticate(user=self.user)
        data = self._make_data(url="https://www.uta.edu.au")
        response = self.client.post('/rest_api/organisations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._check_data(data, response.data)
        self.assertNotIn('vetted_by', response.data)
        self.assertNotIn('proposed_by', response.data)
        org = models.Organisation.objects.get(pk=response.data['id'])
        self.assertEqual(self.user.keystone_user_id, org.proposed_by)
        self.assertIsNone(org.vetted_by)

    def test_propose_missing_field(self):
        self.client.force_authenticate(user=self.user)
        data = self._make_data(
            short_name='WTF',
            full_name='',
            url='https://wtf.org'
        )
        response = self.client.post('/rest_api/organisations/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('full_name', response.data)

    def test_propose_bad_country(self):
        self.client.force_authenticate(user=self.user)
        data = self._make_data(
            short_name='WTF',
            full_name='World Triffid Foundation',
            url='https://wtf.org',
            country='xx'
        )
        response = self.client.post('/rest_api/organisations/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('country', response.data)

    def test_propose_extra_fields(self):
        self.client.force_authenticate(user=self.user)
        data = self._make_data(
            short_name='WTF',
            full_name='World Triffid Foundation',
            url='https://wtf.org',
            ror_id='https://ror.org/xyzzy',
            enabled=False,
        )
        response = self.client.post('/rest_api/organisations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('', response.data['ror_id'])
        self.assertTrue(response.data['enabled'])

    def test_propose_duplicate(self):
        self.client.force_authenticate(user=self.user)
        data = self._make_data(
            short_name='QCIF',
            full_name='Queensland Cyber Infrastructure Foundation',
            url='https://qcif.edu.au'
        )
        response = self.client.post('/rest_api/organisations/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            'full_name': [
                exceptions.ErrorDetail(
                    string='An Organisation with this full name '
                    'already exists.', code='invalid')]},
            response.data)

    def test_propose_rejected(self):
        self.client.force_authenticate(user=self.user)
        data = self._make_data(
            short_name='UWW',
            full_name='University of Woop Woop',
            url='https://uww.edu.au'
        )
        response = self.client.post('/rest_api/organisations/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            'full_name': [
                exceptions.ErrorDetail(
                    string='An Organisation with this full name '
                    'has already been rejected.', code='invalid')]},
            response.data)

    def test_patch_as_anon(self):
        data = self._make_data(url="https://www.uta.edu.au")
        response = self.client.patch('/rest_api/organisations/1/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_as_user(self):
        self.client.force_authenticate(user=self.user)
        data = self._make_data(url="https://www.uta.edu.au")
        response = self.client.patch('/rest_api/organisations/1/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = self._make_data(url="https://www.uta.edu.au")
        response = self.client.patch('/rest_api/organisations/1/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        org = models.Organisation.objects.get(pk=1)
        self.assertEqual("https://www.uta.edu.au", org.url)
