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

from rest_framework import status

from nectar_dashboard.rcallocation import models

from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories


@mock.patch('openstack_auth.utils.is_token_valid', new=lambda x, y=None: True)
class QuotaTests(base.AllocationAPITest):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.zone = factories.ZoneFactory(name='testzone')
        self.service_type = factories.ServiceTypeFactory(
            catalog_name='test_st'
        )
        self.service_type.zones.add(self.zone)
        self.resource = factories.ResourceFactory(
            quota_name='test_resource', service_type=self.service_type
        )
        self.quota_group = factories.QuotaGroupFactory(
            allocation=self.allocation,
            service_type=self.service_type,
            zone=self.zone,
        )
        self.quota = factories.QuotaFactory(
            group=self.quota_group, resource=self.resource
        )

    def _get_quotas(self, user):
        return models.Quota.objects.filter(
            group__allocation__contact_email=user.username
        )

    def test_list_quotas(self):
        self.client.force_authenticate(user=self.user)
        factories.AllocationFactory.create(
            contact_email=self.user.username, create_quotas=True
        )
        response = self.client.get('/rest_api/quotas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self._get_quotas(self.user).count(), len(response.data['results'])
        )

    def test_list_quotas_for_allocation(self):
        self.client.force_authenticate(user=self.user)
        factories.AllocationFactory.create(
            contact_email=self.user.username, create_quotas=True
        )
        factories.AllocationFactory.create(
            contact_email='otheruser', create_quotas=True
        )
        factories.AllocationFactory.create(
            contact_email='otheruser2', create_quotas=True
        )
        response = self.client.get(
            f'/rest_api/quotas/?group__allocation={self.allocation.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            models.Quota.objects.filter(
                group__allocation=self.allocation
            ).count(),
            len(response.data['results']),
        )

    def test_list_quotas_unauthenticated(self):
        response = self.client.get('/rest_api/quotas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            models.Quota.objects.count(), len(response.data['results'])
        )

    def test_list_quotas_negative(self):
        self.client.force_authenticate(user=self.user)
        factories.AllocationFactory.create(
            contact_email='other@example.com', create_quotas=True
        )
        response = self.client.get('/rest_api/quotas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self._get_quotas(self.user).count(), len(response.data['results'])
        )

    def test_list_quotas_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        factories.AllocationFactory.create(
            contact_email='foo@example.com', create_quotas=True
        )
        factories.AllocationFactory.create(
            contact_email='bar@example.com', create_quotas=True
        )
        response = self.client.get('/rest_api/quotas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            models.Quota.objects.count(), len(response.data['results'])
        )

    def test_get_quota(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/rest_api/quotas/{self.quota.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.quota.id, response.data['id'])

    def test_get_quota_unauthenticated(self):
        response = self.client.get(f'/rest_api/quotas/{self.quota.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_quota_negative(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/rest_api/quotas/{self.quota.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_quota_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/rest_api/quotas/{self.quota.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_quota(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f'/rest_api/quotas/{self.quota.id}/', {'resource': 4}
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_quota(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/rest_api/quotas/{self.quota.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_quota_invalid_state(self):
        self.client.force_authenticate(user=self.user)
        self.allocation.status = models.AllocationRequest.APPROVED
        self.allocation.save()
        quota = self.allocation.quotas.all()[0]
        response = self.client.delete(f'/rest_api/quotas/{quota.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_quota_negative(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/rest_api/quotas/{self.quota.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        resource = factories.ResourceFactory(
            quota_name='test_resource2', service_type=self.service_type
        )
        data = {
            'allocation': self.allocation.id,
            'resource': resource.id,
            'zone': self.zone.name,
            'quota': 20,
            'requested_quota': 10,
        }
        response = self.client.post('/rest_api/quotas/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        quota = models.Quota.objects.get(id=response.data['id'])
        # Use the same service type to quota group should be existing
        self.assertEqual(self.quota_group.id, quota.group.id)

    def test_create_unlimited_managed(self):
        self.client.force_authenticate(user=self.user)
        resource = factories.ResourceFactory(
            quota_name='test_resource2', service_type=self.service_type
        )
        data = {
            'allocation': self.allocation.id,
            'resource': resource.id,
            'zone': self.zone.name,
            'quota': -1,
            'requested_quota': -1,
        }
        response = self.client.post('/rest_api/quotas/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_unlimited_unmanaged(self):
        self.client.force_authenticate(user=self.user)
        resource = factories.ResourceFactory(
            quota_name='test_resource2', service_type=self.service_type
        )
        data = {
            'allocation': self.allocation.id,
            'resource': resource.id,
            'zone': self.zone.name,
            'quota': -1,
            'requested_quota': -1,
        }
        self.allocation.managed = False
        self.allocation.save()
        response = self.client.post('/rest_api/quotas/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        quota = models.Quota.objects.get(id=response.data['id'])
        # Use the same service type to quota group should be existing
        self.assertEqual(self.quota_group.id, quota.group.id)

    def test_create_approver(self):
        self.client.force_authenticate(user=self.approver_user)
        resource = factories.ResourceFactory(
            quota_name='test_resource2', service_type=self.service_type
        )
        data = {
            'allocation': self.allocation.id,
            'resource': resource.id,
            'zone': self.zone.name,
            'quota': 20,
            'requested_quota': 10,
        }
        response = self.client.post('/rest_api/quotas/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        quota = models.Quota.objects.get(id=response.data['id'])
        # Use the same service type to quota group should be existing
        self.assertEqual(self.quota_group.id, quota.group.id)

    def test_create_invalid_requested_quota(self):
        self.client.force_authenticate(user=self.user)
        resource = factories.ResourceFactory(
            quota_name='test_resource2', service_type=self.service_type
        )
        data = {
            'allocation': self.allocation.id,
            'resource': resource.id,
            'zone': self.zone.name,
            'quota': 20,
            'requested_quota': -2,
        }
        response = self.client.post('/rest_api/quotas/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_quota(self):
        self.client.force_authenticate(user=self.user)
        resource = factories.ResourceFactory(
            quota_name='test_resource2', service_type=self.service_type
        )
        data = {
            'allocation': self.allocation.id,
            'resource': resource.id,
            'zone': self.zone.name,
            'quota': -2,
            'requested_quota': 10,
        }
        response = self.client.post('/rest_api/quotas/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'allocation': self.allocation.id,
            'resource': self.resource.id,
            'zone': self.zone.name,
            'quota': 20,
            'requested_quota': 10,
        }
        response = self.client.post('/rest_api/quotas/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_zone(self):
        zone = factories.ZoneFactory(name='testzone2')
        self.client.force_authenticate(user=self.user)

        data = {
            'allocation': self.allocation.id,
            'resource': self.resource.id,
            'zone': zone.name,
            'quota': 20,
            'requested_quota': 10,
        }
        response = self.client.post('/rest_api/quotas/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_unauthenticated(self):
        resource = factories.ResourceFactory(
            quota_name='test_resource2', service_type=self.service_type
        )
        data = {
            'allocation': self.allocation.id,
            'resource': resource.id,
            'zone': self.zone.name,
            'quota': 20,
            'requested_quota': 10,
        }
        response = self.client.post('/rest_api/quotas/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
