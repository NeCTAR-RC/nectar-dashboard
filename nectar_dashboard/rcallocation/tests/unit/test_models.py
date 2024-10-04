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

from django.core.exceptions import ValidationError
from django.utils import timezone

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories


class AllocationModelTestCase(base.BaseTestCase):
    def test_save_updates_timestamps(self):
        now = timezone.now()

        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.APPROVED
        )
        self.assertTrue(allocation.submit_date)
        self.assertTrue(allocation.modified_time)
        self.assertTrue(allocation.submit_date.year == now.year)
        self.assertTrue(allocation.modified_time >= now)

        # (Just making sure that the test's assumptions about clock
        # precision are valid.
        now2 = timezone.now()
        self.assertTrue(now2 > now)

        allocation.save()
        self.assertTrue(allocation.modified_time > now2)

    def test_save_without_updating_timestamps(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.APPROVED
        )
        last_mod = allocation.modified_time

        allocation.save_without_updating_timestamps()

        self.assertTrue(allocation.modified_time == last_mod)
        allocation = models.AllocationRequest.objects.get(id=allocation.id)
        self.assertTrue(allocation.modified_time == last_mod)

    def test_can_be_amended(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.APPROVED
        )

        self.assertTrue(allocation.can_be_amended())

    def test_can_be_amended_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False,
            status=models.AllocationRequest.APPROVED,
            managed=False,
        )

        self.assertFalse(allocation.can_be_amended())

    def test_can_be_edited(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED
        )

        self.assertTrue(allocation.can_be_edited())

    def test_can_be_edited_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False,
            status=models.AllocationRequest.SUBMITTED,
            managed=False,
        )

        self.assertFalse(allocation.can_be_edited())

    def test_can_user_edit(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED
        )

        self.assertTrue(allocation.can_user_edit())

    def test_can_user_edit_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False,
            status=models.AllocationRequest.SUBMITTED,
            managed=False,
        )

        self.assertFalse(allocation.can_user_edit())

    def test_can_user_edit_amendment(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.UPDATE_PENDING
        )

        self.assertTrue(allocation.can_user_edit_amendment())

    def test_can_user_edit_amendment_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False,
            status=models.AllocationRequest.UPDATE_PENDING,
            managed=False,
        )

        self.assertFalse(allocation.can_user_edit_amendment())

    def test_can_be_rejected(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED
        )

        self.assertTrue(allocation.can_be_rejected())

    def test_can_be_rejected_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False,
            status=models.AllocationRequest.SUBMITTED,
            managed=False,
        )

        self.assertFalse(allocation.can_be_rejected())

    def test_can_be_approved(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED
        )

        self.assertTrue(allocation.can_be_approved())

    def test_can_be_approved_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False,
            status=models.AllocationRequest.SUBMITTED,
            managed=False,
        )

        self.assertFalse(allocation.can_be_approved())

    def test_validate_doi(self):
        models.VALIDATE_DOI("10.100000/HelloMum")
        with self.assertRaises(ValidationError):
            models.VALIDATE_DOI("10.100000/Hello Mum")
        with self.assertRaises(ValidationError):
            models.VALIDATE_DOI("10.100000/Hello\tMum")

    def test_quota_list_no_bundle(self):
        allocation = factories.AllocationFactory.create(bundle=None)
        expected = [
            {'quota': 0, 'resource': 'volume.gigabytes', 'zone': 'melbourne'},
            {'quota': 0, 'resource': 'volume.gigabytes', 'zone': 'monash'},
            {'quota': 0, 'resource': 'compute.cores', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'compute.instances', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'network.router', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'network.network', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'network.loadbalancer', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'network.floatingip', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'object.object', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'rating.budget', 'zone': 'nectar'},
        ]
        self.assertEqual(expected, allocation.quota_list())

    def test_quota_list_bundle(self):
        gold = models.Bundle.objects.get(name='gold')
        allocation = factories.AllocationFactory.create(
            create_quotas=False, bundle=gold
        )

        expected = [
            {'quota': 200, 'resource': 'object.object', 'zone': 'nectar'},
            {'quota': 200, 'resource': 'compute.cores', 'zone': 'nectar'},
            {'quota': 200, 'resource': 'compute.instances', 'zone': 'nectar'},
            {'quota': 2000, 'resource': 'compute.ram', 'zone': 'nectar'},
            {'quota': 16000, 'resource': 'rating.budget', 'zone': 'nectar'},
            {'quota': 20, 'resource': 'network.router', 'zone': 'nectar'},
            {'quota': 20, 'resource': 'network.network', 'zone': 'nectar'},
            {
                'quota': 20,
                'resource': 'network.loadbalancer',
                'zone': 'nectar',
            },
            {'quota': 20, 'resource': 'network.floatingip', 'zone': 'nectar'},
        ]
        self.assertEqual(expected, allocation.quota_list())

    def test_quota_list_bundle_with_overrides(self):
        bronze = models.Bundle.objects.get(name='bronze')
        allocation = factories.AllocationFactory.create(bundle=bronze)
        expected = [
            {'quota': 0, 'resource': 'object.object', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'compute.cores', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'compute.instances', 'zone': 'nectar'},
            {'quota': 500, 'resource': 'compute.ram', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'rating.budget', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'network.router', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'network.network', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'network.loadbalancer', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'network.floatingip', 'zone': 'nectar'},
            {'quota': 0, 'resource': 'volume.gigabytes', 'zone': 'melbourne'},
            {'quota': 0, 'resource': 'volume.gigabytes', 'zone': 'monash'},
        ]
        self.assertEqual(expected, allocation.quota_list())

    def test_su_budget_no_bundle(self):
        allocation = factories.AllocationFactory.create(
            bundle=None, create_quotas=False
        )
        budget_resource = models.Resource.objects.get_by_codename(
            'rating.budget'
        )
        zone = models.Zone.objects.get(name='nectar')
        qg = models.QuotaGroup.objects.create(
            allocation=allocation,
            zone=zone,
            service_type=budget_resource.service_type,
        )
        models.Quota.objects.create(
            group=qg, resource=budget_resource, quota=25, requested_quota=20
        )
        self.assertEqual(25, allocation.su_budget)

    def test_su_budget_override(self):
        bronze = models.Bundle.objects.get(name='bronze')
        allocation = factories.AllocationFactory.create(
            bundle=bronze, create_quotas=False
        )
        budget_resource = models.Resource.objects.get_by_codename(
            'rating.budget'
        )
        zone = models.Zone.objects.get(name='nectar')
        qg = models.QuotaGroup.objects.create(
            allocation=allocation,
            zone=zone,
            service_type=budget_resource.service_type,
        )
        models.Quota.objects.create(
            group=qg, resource=budget_resource, quota=13453, requested_quota=20
        )
        self.assertEqual(13453, allocation.su_budget)

    def test_su_budget_none(self):
        allocation = factories.AllocationFactory.create(
            bundle=None, create_quotas=False
        )
        self.assertIsNone(allocation.su_budget)

    def test_su_budget_bundle(self):
        gold = models.Bundle.objects.get(name='gold')
        allocation = factories.AllocationFactory.create(
            bundle=gold, create_quotas=False
        )
        self.assertEqual(16000, allocation.su_budget)

    def test_get_quota_does_not_exist(self):
        allocation = factories.AllocationFactory.create(create_quotas=False)
        self.assertIsNone(allocation.get_quota('rating.budget'))

    def test_get_quota_exists(self):
        allocation = factories.AllocationFactory.create()
        self.assertEqual(0, allocation.get_quota('rating.budget'))


class QuotaGroupModelTestCase(base.BaseTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # Create an allocation which will in turn create some quotas
        self.allocation = factories.AllocationFactory.create()

    def test_all_quotas_manager(self):
        expected = models.Quota.objects.filter(
            group__allocation=self.allocation
        )
        quota_list = self.allocation.quotas.all_quotas()
        self.assertCountEqual(expected, quota_list)
