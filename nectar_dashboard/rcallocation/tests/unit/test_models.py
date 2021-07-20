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

from openstack_dashboard.test import helpers

from nectar_dashboard.rcallocation import models

from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories


class ModelsTestCase(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.factory_setup()

    def test_save_updates_timestamps(self):
        now = timezone.now()

        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.APPROVED)
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
            create_quotas=False, status=models.AllocationRequest.APPROVED)
        last_mod = allocation.modified_time

        allocation.save_without_updating_timestamps()

        self.assertTrue(allocation.modified_time == last_mod)
        allocation = models.AllocationRequest.objects.get(id=allocation.id)
        self.assertTrue(allocation.modified_time == last_mod)

    def test_can_be_amended(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.APPROVED)

        self.assertTrue(allocation.can_be_amended())

    def test_can_be_amended_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.APPROVED,
            managed=False)

        self.assertFalse(allocation.can_be_amended())

    def test_can_be_edited(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED)

        self.assertTrue(allocation.can_be_edited())

    def test_can_be_edited_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED,
            managed=False)

        self.assertFalse(allocation.can_be_edited())

    def test_can_admin_edit(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED)

        self.assertTrue(allocation.can_admin_edit())

    def test_can_admin_edit_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED,
            managed=False)

        self.assertFalse(allocation.can_admin_edit())

    def test_can_user_edit(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED)

        self.assertTrue(allocation.can_user_edit())

    def test_can_user_edit_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED,
            managed=False)

        self.assertFalse(allocation.can_user_edit())

    def test_can_user_edit_amendment(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False,
            status=models.AllocationRequest.UPDATE_PENDING)

        self.assertTrue(allocation.can_user_edit_amendment())

    def test_can_user_edit_amendment_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False,
            status=models.AllocationRequest.UPDATE_PENDING,
            managed=False)

        self.assertFalse(allocation.can_user_edit_amendment())

    def test_can_be_rejected(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED)

        self.assertTrue(allocation.can_be_rejected())

    def test_can_be_rejected_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED,
            managed=False)

        self.assertFalse(allocation.can_be_rejected())

    def test_can_be_approved(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED)

        self.assertTrue(allocation.can_be_approved())

    def test_can_be_approved_not_managed(self):
        allocation = factories.AllocationFactory.create(
            create_quotas=False, status=models.AllocationRequest.SUBMITTED,
            managed=False)

        self.assertFalse(allocation.can_be_approved())

    def test_validate_doi(self):
        models.VALIDATE_DOI("10.100000/HelloMum")
        with self.assertRaises(ValidationError):
            models.VALIDATE_DOI("10.100000/Hello Mum")
        with self.assertRaises(ValidationError):
            models.VALIDATE_DOI("10.100000/Hello\tMum")
