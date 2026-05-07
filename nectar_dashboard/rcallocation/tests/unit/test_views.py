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

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories
from nectar_dashboard.rcallocation import views


class _StubView(views.QuotaFormMixin):
    def __init__(self, allocation):
        self.object = allocation


class GetQuotasInitialBundleSeedTestCase(base.BaseTestCase):
    """Regression tests for NECTAR-15070.

    A bundle allocation has no Quota rows for its single-zone resources
    (set_quotas() deletes them when a bundle is set), so before the fix the
    amend/edit form rendered those fields empty and silently zeroed them on
    save when the user picked "custom".
    """

    def test_bundle_allocation_seeds_initial_from_bundle_quotas(self):
        gold = models.Bundle.objects.get(name='gold')
        allocation = factories.AllocationFactory.create(
            create_quotas=False,
            bundle=gold,
            status=models.AllocationRequest.APPROVED,
        )

        initial = _StubView(allocation).get_quotas_initial()

        # rating.budget is covered by the next test — its initial value
        # comes from AllocationRequest.su_budget rather than the
        # BundleQuota row, mirroring AllocationRequest.quota_list().
        for bq in gold.bundlequota_set.exclude(
            resource__service_type__catalog_name='rating'
        ):
            key = f"quota-{bq.resource.codename}__{gold.zone.name}"
            self.assertEqual(initial.get(key), bq.quota)

    def test_bundle_allocation_seeds_rating_budget_from_su_budget(self):
        gold = models.Bundle.objects.get(name='gold')
        allocation = factories.AllocationFactory.create(
            create_quotas=False,
            bundle=gold,
            status=models.AllocationRequest.APPROVED,
        )

        initial = _StubView(allocation).get_quotas_initial()

        self.assertEqual(
            initial.get(f"quota-rating.budget__{gold.zone.name}"),
            allocation.su_budget,
        )
