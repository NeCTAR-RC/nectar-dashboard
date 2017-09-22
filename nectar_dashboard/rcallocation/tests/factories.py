from datetime import date, timedelta
import factory
from factory import fuzzy

from nectar_dashboard.rcallocation import for_choices, project_duration_choices, \
    allocation_home_choices, grant_type


FOR_CHOICES = dict(for_choices.FOR_CHOICES)
DURATION_CHOICES = dict(project_duration_choices.DURATION_CHOICE)
ALLOCATION_HOMES = dict(allocation_home_choices.ALLOC_HOME_CHOICE)
GRANT_TYPES = dict(grant_type.GRANT_TYPES)

for_code = fuzzy.FuzzyChoice(FOR_CHOICES.keys())
_1_year = date.today() + timedelta(days=365)
_3_years = date.today() + timedelta(days=365 * 3)
duration = fuzzy.FuzzyChoice(DURATION_CHOICES.keys())
percent = fuzzy.FuzzyInteger(1, 100)
alloc_home = fuzzy.FuzzyChoice(ALLOCATION_HOMES.keys())
grant_types = fuzzy.FuzzyChoice(GRANT_TYPES.keys())


class QuotaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Quota'
    requested_quota = fuzzy.FuzzyInteger(1, 100000)
    resource = 'volume'
    quota = 0


class InstitutionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Institution'
    name = 'Monash'


class PublicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Publication'
    publication = 'publication testing'


class GrantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.Grant'
    grant_type = grant_types
    funding_body_scheme = 'ARC funding scheme'
    grant_id = 'arc-grant-0001'
    first_year_funded = 2015
    total_funding = 20000


class InvestigatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.ChiefInvestigator'
    title = 'Prof.'
    given_name = 'MeRC'
    surname = 'Monash'
    email = 'merc.monash@monash.edu'
    institution = 'Monash University'
    additional_researchers = 'None'


class AllocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'rcallocation.AllocationRequest'

    created_by = fuzzy.FuzzyText()
    contact_email = 'test@example.com'
    start_date = fuzzy.FuzzyDate(date.today(), _1_year)
    primary_instance_type = ' '
    use_case = fuzzy.FuzzyText()
    usage_patterns = fuzzy.FuzzyText()
    geographic_requirements = fuzzy.FuzzyText()
    allocation_home = alloc_home
    project_description = fuzzy.FuzzyText()
    field_of_research_1 = for_code
    field_of_research_2 = for_code
    field_of_research_3 = for_code
    for_percentage_1 = 50
    for_percentage_2 = 40
    for_percentage_3 = 10
    estimated_number_users = 1000
    funding_national_percent = percent
    funding_node = 'monash'
    nectar_support = 'nectar supporting'
    ncris_support = 'ncris supporting'

    @classmethod
    def create(cls, **kwargs):
        zones = ['melbourne', 'qld', 'monash']
        attrs = cls.attributes(create=True, extra=kwargs)
        allocation = cls._generate(True, attrs)
        for zone in zones:
            QuotaFactory(allocation=allocation, zone=zone)
        return allocation
