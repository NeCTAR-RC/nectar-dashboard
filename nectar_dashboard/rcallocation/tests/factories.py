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

import datetime

import factory
from factory import fuzzy

from nectar_dashboard.rcallocation import allocation_home_choices
from nectar_dashboard.rcallocation import forcodes
from nectar_dashboard.rcallocation import grant_type
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import project_duration_choices


DURATION_CHOICES = dict(project_duration_choices.DURATION_CHOICE)
ALLOCATION_HOMES = dict(allocation_home_choices.ALLOC_HOME_CHOICE[1:-1])
GRANT_TYPES = dict(grant_type.GRANT_TYPES)
GRANT_SUBTYPES = dict(grant_type.GRANT_SUBTYPES)
ALL_SITES = ['uom', 'qcif', 'monash', 'ardc']

for_code = fuzzy.FuzzyChoice(forcodes.FOR_CODES[forcodes.FOR_SERIES].keys())
_1_year = datetime.date.today() + datetime.timedelta(days=365)
_3_years = datetime.date.today() + datetime.timedelta(days=365 * 3)
duration = fuzzy.FuzzyChoice(DURATION_CHOICES.keys())
percent = fuzzy.FuzzyInteger(1, 100)
alloc_home = fuzzy.FuzzyChoice(ALLOCATION_HOMES.keys())
grant_types = fuzzy.FuzzyChoice(GRANT_TYPES.keys())
grant_subtypes = fuzzy.FuzzyChoice(GRANT_SUBTYPES.keys())
site = fuzzy.FuzzyChoice(models.Site.objects.get(name=s) for s in ALL_SITES)


def get_active_usage_types():
    return models.UsageType.objects.filter(enabled=True)


class ZoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Zone'
        django_get_or_create = ('name',)

    display_name = fuzzy.FuzzyText()


class ServiceTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.ServiceType'
        django_get_or_create = ('catalog_name',)

    name = fuzzy.FuzzyText()
    description = fuzzy.FuzzyText()

    @factory.post_generation
    def zones(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for zone in extracted:
                self.zones.add(zone)


class ResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Resource'
        django_get_or_create = ('service_type', 'quota_name')

    name = fuzzy.FuzzyText()
    service_type = factory.SubFactory(ServiceTypeFactory)
    unit = fuzzy.FuzzyText()


class QuotaGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.QuotaGroup'


class QuotaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Quota'

    requested_quota = fuzzy.FuzzyInteger(1, 100000)
    quota = 0


class BundleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Bundle'

    name = fuzzy.FuzzyText()
    description = fuzzy.FuzzyText()
    order = fuzzy.FuzzyInteger(1, 100000)


class BundleQuotaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.BundleQuota'

    quota = fuzzy.FuzzyInteger(1, 100000)


class OrganisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Organisation'

    short_name = fuzzy.FuzzyText()
    full_name = fuzzy.FuzzyText()
    enabled = True
    ror_id = ''
    vetted_by = None
    proposed_by = ''
    country = 'AU'


class PublicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Publication'

    publication = 'publication testing'


class GrantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Grant'

    grant_type = grant_types
    grant_subtype = grant_subtypes
    funding_body_scheme = 'ARC funding scheme'
    grant_id = 'arc-grant-0001'
    first_year_funded = 2015
    last_year_funded = 2017
    total_funding = 20000


class ARDCSupportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.ARDCSupport'

    name = fuzzy.FuzzyText()
    short_name = fuzzy.FuzzyText()
    project = fuzzy.FuzzyChoice([False, True])
    enabled = True
    rank = 100
    explain = False


class NCRISFacilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.NCRISFacility'

    name = fuzzy.FuzzyText()
    short_name = fuzzy.FuzzyText()


class InvestigatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.ChiefInvestigator'

    # The allocation and primary_organization cannot be defaulted.

    title = 'Prof.'
    given_name = 'MeRC'
    surname = 'Monash'
    email = 'merc.monash@monash.edu'
    additional_researchers = 'None'


class AllocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.AllocationRequest'

    created_by = fuzzy.FuzzyText()
    contact_email = 'test@example.com'
    use_case = fuzzy.FuzzyText()
    usage_patterns = fuzzy.FuzzyText()
    geographic_requirements = fuzzy.FuzzyText()
    project_description = fuzzy.FuzzyText()
    field_of_research_1 = for_code
    field_of_research_2 = for_code
    field_of_research_3 = for_code
    for_percentage_1 = 50
    for_percentage_2 = 40
    for_percentage_3 = 10
    associated_site = site

    @classmethod
    def create(
        cls,
        create_quotas=True,
        only_requestable=True,
        quota_value=0,
        modified_time=None,
        submit_date=None,
        **kwargs,
    ):
        usage_types = kwargs.pop('usage_types', None)
        ncris_facilities = kwargs.pop('ncris_facilities', [])
        ardc_support = kwargs.pop('ardc_support', [])
        supported_organisations = kwargs.pop(
            'supported_organisations', ['Monash']
        )
        attrs = cls.attributes(create=True, extra=kwargs)
        allocation = cls._generate(True, attrs)

        # Override the effects of the 'auto_*' updates on date / timestamps
        manager = models.AllocationRequest.objects
        if modified_time is not None:
            manager.filter(id=allocation.id).update(
                modified_time=modified_time
            )
            allocation.modified_time = modified_time
        if submit_date is not None:
            manager.filter(id=allocation.id).update(submit_date=submit_date)
            allocation.submit_date = submit_date

        if usage_types is None:
            for u in get_active_usage_types():
                allocation.usage_types.add(u)
        else:
            for name in usage_types:
                u = models.UsageType.objects.get(name=name)
                allocation.usage_types.add(u)

        for name in supported_organisations:
            o = models.Organisation.objects.get(short_name=name)
            allocation.supported_organisations.add(o)

        for name in ncris_facilities:
            f = models.NCRISFacility.objects.get(short_name=name)
            allocation.ncris_facilities.add(f)

        for name in ardc_support:
            a = models.ARDCSupport.objects.get(short_name=name)
            allocation.ardc_support.add(a)

        if create_quotas:
            monash = models.Zone.objects.get(name='monash')
            melbourne = models.Zone.objects.get(name='melbourne')
            nectar = models.Zone.objects.get(name='nectar')

            volume_st = models.ServiceType.objects.get(catalog_name='volume')
            object_st = models.ServiceType.objects.get(catalog_name='object')
            compute_st = models.ServiceType.objects.get(catalog_name='compute')
            network_st = models.ServiceType.objects.get(catalog_name='network')
            rating_st = models.ServiceType.objects.get(catalog_name='rating')

            objects = models.Resource.objects.get(
                quota_name='object', service_type=object_st
            )
            volumes = models.Resource.objects.get(
                quota_name='gigabytes', service_type=volume_st
            )
            cores = models.Resource.objects.get(
                quota_name='cores', service_type=compute_st
            )
            instances = models.Resource.objects.get(
                quota_name='instances', service_type=compute_st
            )
            ram = models.Resource.objects.get(
                quota_name='ram', service_type=compute_st
            )
            budget = models.Resource.objects.get(
                quota_name='budget', service_type=rating_st
            )
            router = models.Resource.objects.get(
                quota_name='router', service_type=network_st
            )
            network = models.Resource.objects.get(
                quota_name='network', service_type=network_st
            )
            loadbalancer = models.Resource.objects.get(
                quota_name='loadbalancer', service_type=network_st
            )
            floatingip = models.Resource.objects.get(
                quota_name='floatingip', service_type=network_st
            )

            group_volume_monash = QuotaGroupFactory(
                allocation=allocation, service_type=volume_st, zone=monash
            )
            group_volume_melbourne = QuotaGroupFactory(
                allocation=allocation, service_type=volume_st, zone=melbourne
            )
            group_object = QuotaGroupFactory(
                allocation=allocation, service_type=object_st, zone=nectar
            )
            group_compute = QuotaGroupFactory(
                allocation=allocation, service_type=compute_st, zone=nectar
            )
            group_rating = QuotaGroupFactory(
                allocation=allocation, service_type=rating_st, zone=nectar
            )
            group_network = QuotaGroupFactory(
                allocation=allocation, service_type=network_st, zone=nectar
            )
            QuotaFactory(
                group=group_object, resource=objects, quota=quota_value
            )
            QuotaFactory(
                group=group_volume_monash, resource=volumes, quota=quota_value
            )
            QuotaFactory(
                group=group_volume_melbourne,
                resource=volumes,
                quota=quota_value,
            )
            QuotaFactory(
                group=group_compute, resource=cores, quota=quota_value
            )
            QuotaFactory(
                group=group_compute, resource=instances, quota=quota_value
            )
            if not only_requestable:
                QuotaFactory(
                    group=group_compute, resource=ram, quota=quota_value
                )
            QuotaFactory(
                group=group_rating, resource=budget, quota=quota_value
            )
            QuotaFactory(
                group=group_network, resource=router, quota=quota_value
            )
            QuotaFactory(
                group=group_network, resource=network, quota=quota_value
            )
            QuotaFactory(
                group=group_network, resource=loadbalancer, quota=quota_value
            )
            QuotaFactory(
                group=group_network, resource=floatingip, quota=quota_value
            )

        return allocation
