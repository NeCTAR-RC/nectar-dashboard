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

from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories
from nectar_dashboard.rcallocation import views


class SetQuotasLocationSpecificTestCase(base.BaseTestCase):
    """Regression tests for set_quotas() and the location_specific flag.

    set_quotas() decides per-quota whether to persist the user's value
    or delete the existing Quota row. The decision used to depend on
    zone count (a service was treated as location-specific only when
    it had more than one zone), which gave the wrong answer for a
    single-zone location-specific service: with a bundle selected, its
    quota would be silently deleted. The fix routes the decision
    through ServiceType.location_specific.

    The test fixture seeds a single-zone location-specific service
    (catalog_name 'ls-service-type', zone 'pawsey') alongside the
    existing multi-zone ones.

    Matrix covered:
      bundle vs custom (allocation.bundle set vs not)
      toggle on vs off (location-specific quota present vs absent)
    """

    def _bind_form(self, allocation, quota_values):
        """Build an AllocationRequestForm and stamp cleaned_data.

        quota_values is a {(catalog_name, quota_name, zone_name): value}
        mapping for the quota fields we care about. Fields not listed
        default to 0, matching how the form renders an untouched input.
        """
        form = forms.AllocationRequestForm(instance=allocation)
        cleaned = {}
        for field_name, field in form.fields.items():
            if not field_name.startswith('quota-'):
                continue
            key = (
                field.resource.service_type.catalog_name,
                field.resource.quota_name,
                field.zone.name,
            )
            cleaned[field_name] = quota_values.get(key, 0)
        form.cleaned_data = cleaned
        return form

    def _get_quota(self, allocation, catalog_name, zone_name, quota_name):
        try:
            group = models.QuotaGroup.objects.get(
                allocation=allocation,
                zone__name=zone_name,
                service_type__catalog_name=catalog_name,
            )
        except models.QuotaGroup.DoesNotExist:
            return None
        resource = models.Resource.objects.get(
            service_type__catalog_name=catalog_name, quota_name=quota_name
        )
        try:
            return models.Quota.objects.get(group=group, resource=resource)
        except models.Quota.DoesNotExist:
            return None

    def test_bundle_with_location_specific_quota_persists_quota(self):
        """With a bundle selected, an opt-in location-specific value
        must persist.

        Before the fix, set_quotas treated the single-zone location-
        specific service as non-location-specific (because it has only
        one zone) and so deleted the row.
        """
        gold = models.Bundle.objects.get(name='gold')
        allocation = factories.AllocationFactory.create(
            bundle=gold, create_quotas=False
        )
        form = self._bind_form(
            allocation, {('ls-service-type', 'object', 'pawsey'): 500}
        )

        views.QuotaFormMixin.set_quotas(allocation, form)

        ls_quota = self._get_quota(
            allocation, 'ls-service-type', 'pawsey', 'object'
        )
        self.assertIsNotNone(
            ls_quota,
            "Location-specific Quota row should exist when toggle is "
            "on with a bundle",
        )
        self.assertEqual(500, ls_quota.requested_quota)

    def test_bundle_without_location_specific_quota_creates_no_row(self):
        """With a bundle selected and the location-specific toggle off
        (value 0), no Quota row should be created and the other
        behaviour is unchanged."""
        gold = models.Bundle.objects.get(name='gold')
        allocation = factories.AllocationFactory.create(
            bundle=gold, create_quotas=False
        )
        # Quota values dict is empty -> every quota field defaults to 0,
        # which is the "toggle off / nothing entered" case.
        form = self._bind_form(allocation, {})

        views.QuotaFormMixin.set_quotas(allocation, form)

        self.assertIsNone(
            self._get_quota(allocation, 'ls-service-type', 'pawsey', 'object'),
            "Location-specific Quota row should NOT exist when toggle is off",
        )
        # No non-location-specific Quota rows should exist either: with
        # a bundle set, set_quotas defers those values to BundleQuota.
        self.assertIsNone(
            self._get_quota(allocation, 'compute', 'nectar', 'cores'),
            "Non-location-specific Quotas must not be created when "
            "bundle is set",
        )

    def test_custom_with_location_specific_quota_persists_quota(self):
        """Without a bundle, an opt-in location-specific value must
        persist."""
        allocation = factories.AllocationFactory.create(
            bundle=None, create_quotas=False
        )
        form = self._bind_form(
            allocation,
            {
                ('ls-service-type', 'object', 'pawsey'): 250,
                ('compute', 'cores', 'nectar'): 64,
            },
        )

        views.QuotaFormMixin.set_quotas(allocation, form)

        ls_quota = self._get_quota(
            allocation, 'ls-service-type', 'pawsey', 'object'
        )
        self.assertIsNotNone(ls_quota)
        self.assertEqual(250, ls_quota.requested_quota)
        # Sanity: the custom (non-location-specific) compute quota
        # persists too — the new path hasn't displaced the existing one.
        compute_quota = self._get_quota(
            allocation, 'compute', 'nectar', 'cores'
        )
        self.assertIsNotNone(compute_quota)
        self.assertEqual(64, compute_quota.requested_quota)

    def test_custom_without_location_specific_quota_creates_no_row(self):
        """Without a bundle and the location-specific toggle off, no
        Quota row is created; other custom quotas keep working as
        before."""
        allocation = factories.AllocationFactory.create(
            bundle=None, create_quotas=False
        )
        form = self._bind_form(
            allocation, {('compute', 'cores', 'nectar'): 16}
        )

        views.QuotaFormMixin.set_quotas(allocation, form)

        self.assertIsNone(
            self._get_quota(allocation, 'ls-service-type', 'pawsey', 'object')
        )
        compute_quota = self._get_quota(
            allocation, 'compute', 'nectar', 'cores'
        )
        self.assertIsNotNone(compute_quota)
        self.assertEqual(16, compute_quota.requested_quota)
