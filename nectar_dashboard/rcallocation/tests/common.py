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

from itertools import chain

from factory import fuzzy

from nectar_dashboard.rcallocation import allocation_home_choices
from nectar_dashboard.rcallocation import forcodes
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import project_duration_choices
from nectar_dashboard.rcallocation.tests import factories


DURATION_CHOICES = dict(project_duration_choices.DURATION_CHOICE)
ALLOCATION_HOMES = dict(allocation_home_choices.ALLOC_HOME_CHOICE[1:-1])
GROUP_NAMES = ['compute', 'object', 'volume', 'network', 'rating']


def model_to_dict(instance, exclude=[]):
    """Copy of django.forms.models.model_to_dict

    Django's version excludes non editable fields which
    we don't want
    """
    opts = instance._meta
    data = {}
    for f in chain(
        opts.concrete_fields, opts.private_fields, opts.many_to_many
    ):
        if f.name in exclude:
            continue
        data[f.name] = f.value_from_object(instance)
    return data


def allocation_to_dict(model):
    allocation = model_to_dict(model, exclude=[])
    allocation['quota'] = model.quota_list()

    allocation['organisation'] = [
        model_to_dict(org, exclude=['id', 'allocation'])
        for org in model.supported_organisations.all()
    ]

    allocation['publication'] = [
        model_to_dict(pub, exclude=['id', 'allocation'])
        for pub in model.publications.all()
    ]

    allocation['grant'] = [
        model_to_dict(grant, exclude=['id', 'allocation'])
        for grant in model.grants.all()
    ]

    allocation['usage_types'] = [
        model_to_dict(usage) for usage in model.usage_types.all()
    ]

    allocation['investigator'] = [
        model_to_dict(inv, exclude=['id', 'allocation'])
        for inv in model.investigators.all()
    ]
    return allocation


def sites_setup():
    for s in factories.ALL_SITES:
        models.Site.objects.get_or_create(name=s, display_name=s)


def get_site(name):
    try:
        return models.Site.objects.get(name=name)
    except models.Site.DoesNotExist:
        return None


def factory_setup():
    sites_setup()
    approvers_setup()
    organisations_setup()
    usage_types_setup()
    melbourne = factories.ZoneFactory(name='melbourne')
    monash = factories.ZoneFactory(name='monash')
    tas = factories.ZoneFactory(name='tas')
    nectar = factories.ZoneFactory(name='nectar')
    disabled_zone = factories.ZoneFactory(name='disabled-zone', enabled=False)
    # Needed for checker tests as we use this zone
    factories.ZoneFactory(name='QRIScloud')

    volume_st = factories.ServiceTypeFactory(catalog_name='volume')
    object_st = factories.ServiceTypeFactory(catalog_name='object')
    compute_st = factories.ServiceTypeFactory(catalog_name='compute')
    network_st = factories.ServiceTypeFactory(catalog_name='network')
    rating_st = factories.ServiceTypeFactory(catalog_name='rating')
    volume_st.zones.add(melbourne)
    volume_st.zones.add(monash)
    volume_st.zones.add(tas)
    volume_st.zones.add(disabled_zone)
    object_st.zones.add(nectar)
    compute_st.zones.add(nectar)
    network_st.zones.add(nectar)
    rating_st.zones.add(nectar)

    factories.ResourceFactory(quota_name='gigabytes', service_type=volume_st)
    objects = factories.ResourceFactory(
        quota_name='object', service_type=object_st
    )
    cores = factories.ResourceFactory(
        quota_name='cores', service_type=compute_st
    )
    instances = factories.ResourceFactory(
        quota_name='instances', service_type=compute_st
    )
    ram = factories.ResourceFactory(
        quota_name='ram', service_type=compute_st, requestable=False
    )
    budget = factories.ResourceFactory(
        quota_name='budget', name="Budget", service_type=rating_st
    )
    router = factories.ResourceFactory(
        quota_name='router', service_type=network_st
    )
    network = factories.ResourceFactory(
        quota_name='network', service_type=network_st
    )
    lb = factories.ResourceFactory(
        quota_name='loadbalancer', service_type=network_st
    )
    fip = factories.ResourceFactory(
        quota_name='floatingip', service_type=network_st
    )

    gold = factories.BundleFactory(name='gold', zone=nectar, su_per_year=16000)
    silver = factories.BundleFactory(
        name='silver', zone=nectar, su_per_year=8000
    )
    bronze = factories.BundleFactory(
        name='bronze', zone=nectar, su_per_year=4000
    )

    factories.BundleQuotaFactory(bundle=gold, resource=objects, quota=200)
    factories.BundleQuotaFactory(bundle=gold, resource=cores, quota=200)
    factories.BundleQuotaFactory(bundle=gold, resource=instances, quota=200)
    factories.BundleQuotaFactory(bundle=gold, resource=ram, quota=2000)
    factories.BundleQuotaFactory(bundle=gold, resource=budget, quota=2000)
    factories.BundleQuotaFactory(bundle=gold, resource=router, quota=20)
    factories.BundleQuotaFactory(bundle=gold, resource=network, quota=20)
    factories.BundleQuotaFactory(bundle=gold, resource=lb, quota=20)
    factories.BundleQuotaFactory(bundle=gold, resource=fip, quota=20)

    factories.BundleQuotaFactory(bundle=silver, resource=objects, quota=100)
    factories.BundleQuotaFactory(bundle=silver, resource=cores, quota=100)
    factories.BundleQuotaFactory(bundle=silver, resource=instances, quota=100)
    factories.BundleQuotaFactory(bundle=silver, resource=ram, quota=1000)
    factories.BundleQuotaFactory(bundle=silver, resource=budget, quota=1000)
    factories.BundleQuotaFactory(bundle=silver, resource=router, quota=10)
    factories.BundleQuotaFactory(bundle=silver, resource=network, quota=10)
    factories.BundleQuotaFactory(bundle=silver, resource=lb, quota=10)
    factories.BundleQuotaFactory(bundle=silver, resource=fip, quota=10)

    factories.BundleQuotaFactory(bundle=bronze, resource=objects, quota=50)
    factories.BundleQuotaFactory(bundle=bronze, resource=cores, quota=50)
    factories.BundleQuotaFactory(bundle=bronze, resource=instances, quota=50)
    factories.BundleQuotaFactory(bundle=bronze, resource=ram, quota=500)
    factories.BundleQuotaFactory(bundle=bronze, resource=budget, quota=500)
    factories.BundleQuotaFactory(bundle=bronze, resource=router, quota=5)
    factories.BundleQuotaFactory(bundle=bronze, resource=network, quota=5)
    factories.BundleQuotaFactory(bundle=bronze, resource=lb, quota=5)
    factories.BundleQuotaFactory(bundle=bronze, resource=fip, quota=5)


def organisations_setup():
    models.Organisation.objects.get_or_create(
        short_name='QCIF',
        full_name='Queensland Cyber Infrastructure Foundation',
        ror_id='https://ror.org/12345678',
        country='AU',
    )
    models.Organisation.objects.get_or_create(
        short_name='Monash',
        full_name='Monash University',
        ror_id='https://ror.org/23456789',
        country='AU',
    )
    models.Organisation.objects.get_or_create(
        short_name='UWW',
        full_name='University of Woop Woop',
        ror_id='',
        country='AU',
        enabled=False,
    )
    models.Organisation.objects.get_or_create(
        short_name=models.ORG_ALL_SHORT_NAME,
        full_name=models.ORG_ALL_FULL_NAME,
        ror_id='',
        country='AU',
    )


def approvers_setup():
    qcif = models.Site.objects.get(name="qcif")
    melbourne = models.Site.objects.get(name="uom")
    (test_user, _) = models.Approver.objects.get_or_create(
        username="test_user", display_name="One"
    )
    (test_user2, _) = models.Approver.objects.get_or_create(
        username="test_user2", display_name="Two"
    )
    models.Approver.objects.get_or_create(
        username="test_user3", display_name="Three"
    )
    test_user.sites.add(qcif)
    test_user2.sites.add(melbourne)


def usage_types_setup():
    # Most of them are set up in migration 0052.  This one is to test
    # handling of disabled UsageTypes
    models.UsageType.objects.get_or_create(name="Disabled", enabled=False)


def get_groups(service_type, allocation=None):
    quota_fuzz = fuzzy.FuzzyInteger(1, 100000)
    try:
        st = models.ServiceType.objects.get(catalog_name=service_type)
    except models.ServiceType.DoesNotExist:
        raise Exception(f"Can't find service type '{service_type}'")
    resources = st.resource_set.filter(requestable=True)
    groups = []
    allocated_zones = []
    if allocation:
        service_type_groups = allocation.quotas.filter(
            service_type__catalog_name=service_type
        )
        for group in service_type_groups:
            quotas = []
            for quota in group.quota_set.filter(resource__requestable=True):
                quotas.append(
                    {
                        'id': quota.id,
                        'requested_quota': quota.requested_quota,
                        'resource': quota.resource.id,
                        'group': group.id,
                        'quota': quota.quota,
                    }
                )
            groups.append(
                {
                    'id': group.id,
                    'zone': group.zone.name,
                    'service_type': group.service_type.catalog_name,
                    'quotas': quotas,
                }
            )
            allocated_zones.append(group.zone.name)
    for zone in st.zones.filter(enabled=True):
        if zone.name in allocated_zones:
            continue
        quotas = []
        for resource in resources:
            if allocation:
                # If this is an existing allocation, set the initial quota to
                # zero for resources it doesn't have an existing quota for. This
                # essentially means when submitting the form we don't ask for
                # any extra resources.
                requested_quota = 0
            else:
                requested_quota = quota_fuzz.fuzz()
            quotas.append(
                {
                    'id': '',
                    'requested_quota': requested_quota,
                    'resource': resource.id,
                    'group': '',
                    'quota': 0,
                }
            )
        groups.append(
            {
                'id': '',
                'zone': zone.name,
                'service_type': st.catalog_name,
                'quotas': quotas,
            }
        )
    return groups


def quota_specs_to_groups(quota_specs):
    # Populate default (zero) quota specs for all known resources
    all_quota_specs = {}
    service_quotas = {}
    groups = {}
    for st in models.ServiceType.objects.all():
        service_quotas[st.catalog_name] = []
        for z in st.zones.all():
            for r in models.Resource.objects.filter(
                service_type=st, requestable=True
            ):
                key = f"{st.catalog_name}_{z.name}_{r.quota_name}"
                all_quota_specs[key] = quota_spec(
                    st.catalog_name, r.quota_name, zone=z.name
                )
    # Override with supplied quota specs
    for qs in quota_specs:
        key = "{}_{}_{}".format(qs['service'], qs['zone'], qs['resource'])
        all_quota_specs[key] = qs
    for qs in all_quota_specs.values():
        st = models.ServiceType.objects.get(catalog_name=qs['service'])
        r = models.Resource.objects.get(
            quota_name=qs['resource'], service_type=st
        )
        service_quotas[st.catalog_name].append(
            {
                'id': '',
                'requested_quota': qs['requested_quota'],
                'quota': qs['quota'],
                'resource': r.id,
                'zone': qs['zone'],
                'group': '',
            }
        )
    for service, quotas in service_quotas.items():
        group_list = []
        for zone in set(map(lambda q: q['zone'], quotas)):
            group_quotas = [q for q in quotas if q['zone'] == zone]
            if len(group_quotas) > 0:
                group_list.append(
                    {
                        'id': '',
                        'zone': zone,
                        'service_type': service,
                        'quotas': group_quotas,
                    }
                )
        groups[service] = group_list
    return groups


def quota_spec(service, resource, quota=0, requested_quota=0, zone='nectar'):
    return {
        'service': service,
        'resource': resource,
        'quota': quota,
        'requested_quota': requested_quota,
        'zone': zone,
    }


def add_quota_forms(
    form,
    all_quotas,
    service_type,
    group_list,
    allocation=None,
    approving=False,
):
    for group in group_list:
        quotas = group.pop('quotas')
        for quota in quotas:
            all_quotas.append(
                {
                    'resource': quota['resource'],
                    'zone': group['zone'],
                    'requested_quota': quota['requested_quota'],
                    'quota': quota['quota'],
                }
            )

            resource = models.Resource.objects.get(id=quota['resource'])
            if allocation and allocation.is_active():
                limit = quota['quota']
            else:
                limit = quota['requested_quota']
            form['quota-{}__{}'.format(resource.codename, group['zone'])] = (
                limit
            )


def next_char(c):
    return chr(ord(c) + 1)


def request_allocation(
    user,
    model=None,
    quota_specs=None,
    supported_organisations=None,
    publications=None,
    grants=None,
    usage_types=None,
    investigators=None,
    approving=False,
    amending=False,
    bundle=None,
):
    """Builds a form and a dict of the allocation it would create
    approving - set to true when testing approving form
    """
    duration = fuzzy.FuzzyChoice(DURATION_CHOICES.keys()).fuzz()
    forp_1 = fuzzy.FuzzyInteger(1, 8).fuzz()
    forp_2 = fuzzy.FuzzyInteger(1, 9 - forp_1).fuzz()
    forp_3 = 10 - (forp_1 + forp_2)
    for_code = fuzzy.FuzzyChoice(
        forcodes.FOR_CODES[forcodes.FOR_SERIES].keys()
    )
    quota = fuzzy.FuzzyInteger(1, 100000)
    site = model.associated_site if model else None

    model_dict = {
        'project_name': fuzzy.FuzzyText().fuzz(),
        'project_description': fuzzy.FuzzyText().fuzz(),
        'estimated_project_duration': duration,
        'field_of_research_1': for_code.fuzz(),
        'field_of_research_2': for_code.fuzz(),
        'field_of_research_3': for_code.fuzz(),
        'for_percentage_1': forp_1 * 10,
        'for_percentage_2': forp_2 * 10,
        'for_percentage_3': forp_3 * 10,
        'usage_patterns': fuzzy.FuzzyText().fuzz(),
        'use_case': fuzzy.FuzzyText().fuzz(),
        'users_figure_type': 'measured',
        'multiple_allocations_check': False,
        'geographic_requirements': fuzzy.FuzzyText().fuzz(),
        'associated_site': site,
        'bundle': bundle,
    }
    if not amending:
        model_dict['direct_access_user_estimate'] = quota.fuzz()
        model_dict['estimated_service_count'] = quota.fuzz()
        model_dict['estimated_service_active_users'] = quota.fuzz()
    else:
        model_dict['direct_access_user_past_year'] = quota.fuzz()
        model_dict['active_service_count'] = quota.fuzz()
        model_dict['service_active_users_past_year'] = quota.fuzz()

    if model:
        groups = {}
        for name in GROUP_NAMES:
            groups[name] = get_groups(name, model)

        publications = [
            {
                'id': pub.id,
                'publication': pub.publication,
                'output_type': pub.output_type,
                'doi': pub.doi,
                'crossref_metadata': pub.crossref_metadata,
            }
            for pub in model.publications.all()
        ]

        grants = [
            {
                'id': grant.id,
                'grant_type': 'arc',
                'grant_subtype': 'arc-discovery',
                'funding_body_scheme': grant.funding_body_scheme,
                'grant_id': grant.grant_id,
                'first_year_funded': 2015,
                'last_year_funded': 2017,
                'total_funding': quota.fuzz(),
            }
            for grant in model.grants.all()
        ]

        investigators = [
            {
                'id': inv.id,
                'title': inv.title,
                'given_name': inv.given_name,
                'surname': inv.surname,
                'email': inv.email,
                'primary_organisation': inv.primary_organisation,
                'additional_researchers': inv.additional_researchers,
            }
            for inv in model.investigators.all()
        ]

        usage_types = model.usage_types.all()

        supported_organisations = model.supported_organisations.all()

    else:
        if quota_specs is None:
            groups = {}
            for name in GROUP_NAMES:
                groups[name] = get_groups(name)
        else:
            groups = quota_specs_to_groups(quota_specs)

        if publications is None:
            publications = [
                {
                    'id': '',
                    'publication': 'publication testing',
                    'output_type': 'AN',
                    'doi': '',
                    'crossref_metadata': '',
                }
            ]

        if grants is None:
            grants = [
                {
                    'id': '',
                    'grant_type': 'arc',
                    'grant_subtype': 'arc-discovery',
                    'funding_body_scheme': 'ARC funding scheme',
                    'grant_id': 'arc-grant-0001',
                    'first_year_funded': 2015,
                    'last_year_funded': 2017,
                    'total_funding': quota.fuzz(),
                }
            ]

        if investigators is None:
            investigators = [
                {
                    'id': '',
                    'title': 'Prof.',
                    'given_name': 'MeRC',
                    'surname': 'Monash',
                    'email': 'merc.monash@monash.edu',
                    'primary_organisation': models.Organisation.objects.get(
                        short_name='Monash'
                    ),
                    'additional_researchers': 'None',
                }
            ]

        if usage_types is None:
            usage_types = factories.get_active_usage_types()

        if supported_organisations is None:
            supported_organisations = [
                models.Organisation.objects.get(short_name='Monash')
            ]

    form = model_dict.copy()
    all_quotas = []

    for name, group_list in groups.items():
        add_quota_forms(
            form,
            all_quotas,
            name,
            group_list,
            allocation=model,
            approving=approving,
        )

    form['publications-INITIAL_FORMS'] = (
        model.publications.count() if model else 0
    )
    form['publications-TOTAL_FORMS'] = len(publications)
    form['publications-MAX_NUM_FORMS'] = 1000

    form['grants-INITIAL_FORMS'] = model.grants.count() if model else 0
    form['grants-TOTAL_FORMS'] = len(grants)
    form['grants-MAX_NUM_FORMS'] = 1000

    form['investigators-INITIAL_FORMS'] = (
        model.investigators.count() if model else 0
    )
    form['investigators-TOTAL_FORMS'] = len(investigators)
    form['investigators-MAX_NUM_FORMS'] = 1000

    for i, pub in enumerate(publications):
        for k, v in pub.items():
            form[f'publications-{i}-{k}'] = v

    for i, grant in enumerate(grants):
        for k, v in grant.items():
            form[f'grants-{i}-{k}'] = v

    for i, inv in enumerate(investigators):
        for k, v in inv.items():
            form[f'investigators-{i}-{k}'] = (
                v.id if k == 'primary_organisation' else v
            )

    form['usage_types'] = [usage.name for usage in usage_types]
    form['supported_organisations'] = ','.join(
        [str(org.id) for org in supported_organisations]
    )
    form['associated_site'] = site or ''
    form['bundle'] = bundle.id if bundle else ''
    if bundle:
        # If bundle we only expect quotas from multi zone resources.
        quotas = []
        for q in all_quotas:
            resource_id = q['resource']
            resource = models.Resource.objects.get(id=resource_id)
            if resource.service_type.is_multizone():
                quotas.append(q)
        model_dict['quotas'] = quotas
    else:
        model_dict['quotas'] = all_quotas

    model_dict['supported_organisations'] = supported_organisations
    model_dict['publications'] = publications
    model_dict['grants'] = grants
    model_dict['investigators'] = investigators
    model_dict['usage_types'] = usage_types
    return model_dict, form
