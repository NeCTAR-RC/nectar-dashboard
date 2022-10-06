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

from django.forms.models import model_to_dict
from factory import fuzzy

from nectar_dashboard.rcallocation import allocation_home_choices
from nectar_dashboard.rcallocation import forcodes
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import project_duration_choices
from nectar_dashboard.rcallocation.tests import factories


DURATION_CHOICES = dict(project_duration_choices.DURATION_CHOICE)
ALLOCATION_HOMES = dict(allocation_home_choices.ALLOC_HOME_CHOICE[1:-1])
GROUP_NAMES = ['compute', 'object', 'volume', 'network', 'rating']


def allocation_to_dict(model):
    allocation = model_to_dict(model)
    quotas = []
    for quota_group in model.quotas.all():
        for quota in quota_group.quota_set.all():
            quota_dict = {'zone': quota_group.zone.name,
                          'resource': quota.resource.codename(),
                          'quota': quota.quota}
            quotas.append(quota_dict)
    allocation['quota'] = quotas

    allocation['institution'] = [
        model_to_dict(inst) for inst in model.institutions.all()]

    allocation['organisation'] = [
        model_to_dict(org) for org in model.supported_organisations.all()]

    allocation['publication'] = [
        model_to_dict(pub) for pub in model.publications.all()]

    allocation['grant'] = [
        model_to_dict(grant) for grant in model.grants.all()]

    allocation['usage'] = [
        usage.name for usage in model.usage_types.all()]

    allocation['investigator'] = [
        model_to_dict(inv) for inv in model.investigators.all()]
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
    organisations_setup()
    melbourne = factories.ZoneFactory(name='melbourne')
    monash = factories.ZoneFactory(name='monash')
    tas = factories.ZoneFactory(name='tas')
    nectar = factories.ZoneFactory(name='nectar')

    volume_st = factories.ServiceTypeFactory(catalog_name='volume')
    object_st = factories.ServiceTypeFactory(catalog_name='object')
    compute_st = factories.ServiceTypeFactory(catalog_name='compute')
    network_st = factories.ServiceTypeFactory(catalog_name='network')
    rating_st = factories.ServiceTypeFactory(catalog_name='rating')
    volume_st.zones.add(melbourne)
    volume_st.zones.add(monash)
    volume_st.zones.add(tas)
    object_st.zones.add(nectar)
    compute_st.zones.add(nectar)
    network_st.zones.add(nectar)
    rating_st.zones.add(nectar)
    factories.ResourceFactory(quota_name='object', service_type=object_st)
    factories.ResourceFactory(quota_name='gigabytes', service_type=volume_st)
    factories.ResourceFactory(quota_name='cores', service_type=compute_st)
    factories.ResourceFactory(quota_name='instances', service_type=compute_st)
    factories.ResourceFactory(quota_name='ram', service_type=compute_st,
                              requestable=False)
    factories.ResourceFactory(quota_name='budget', name="Budget",
                              service_type=rating_st)
    factories.ResourceFactory(quota_name='router', service_type=network_st)
    factories.ResourceFactory(quota_name='network', service_type=network_st)
    factories.ResourceFactory(quota_name='loadbalancer',
                              service_type=network_st)
    factories.ResourceFactory(quota_name='floatingip', service_type=network_st)


def organisations_setup():
    models.Organisation.objects.get_or_create(
        short_name='QCIF',
        full_name='Queensland Cyber Infrastructure Foundation',
        ror_id='https://ror.org/12345678', country='AU')
    models.Organisation.objects.get_or_create(
        short_name='Monash',
        full_name='Monash University',
        ror_id='https://ror.org/23456789', country='AU')
    models.Organisation.objects.get_or_create(
        short_name='UWW',
        full_name='University of Woop Woop',
        ror_id='', country='AU', enabled=False)
    models.Organisation.objects.get_or_create(
        short_name=models.ORG_ALL_SHORT_NAME,
        full_name=models.ORG_ALL_FULL_NAME,
        ror_id='', country='AU')
    models.Organisation.objects.get_or_create(
        short_name=models.ORG_UNKNOWN_SHORT_NAME,
        full_name=models.ORG_UNKNOWN_FULL_NAME,
        ror_id='', country='AU')


def approvers_setup():
    qcif = models.Site.objects.get(name="qcif")
    melbourne = models.Site.objects.get(name="uom")
    (test_user, _) = models.Approver.objects.get_or_create(
        username="test_user", display_name="One")
    (test_user2, _) = models.Approver.objects.get_or_create(
        username="test_user2", display_name="Two")
    models.Approver.objects.get_or_create(
        username="test_user3", display_name="Three")
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
        raise Exception("Can't find service type '%s'" % service_type)
    resources = st.resource_set.filter(requestable=True)
    groups = []
    allocated_zones = []
    if allocation:
        service_type_groups = allocation.quotas.filter(
            service_type__catalog_name=service_type)
        for group in service_type_groups:
            quotas = []
            for quota in group.quota_set.filter(resource__requestable=True):
                quotas.append({'id': quota.id,
                               'requested_quota': quota.requested_quota,
                               'resource': quota.resource.id,
                               'group': group.id,
                               'quota': quota.quota})
            groups.append({'id': group.id,
                           'zone': group.zone.name,
                           'service_type': group.service_type.catalog_name,
                           'quotas': quotas})
            allocated_zones.append(group.zone.name)
    for zone in st.zones.all():
        if zone.name in allocated_zones:
            continue
        quotas = []
        for resource in resources:
            quotas.append(
                {'id': '',
                 'requested_quota': quota_fuzz.fuzz(),
                 'resource': resource.id,
                 'group': '',
                 'quota': 0})
        groups.append({'id': '',
                       'zone': zone.name,
                       'service_type': st.catalog_name,
                       'quotas': quotas})
    return groups


def quota_specs_to_groups(quota_specs):
    # Populate default (zero) quota specs for all known resources
    all_quota_specs = {}
    service_quotas = {}
    groups = {}
    for st in models.ServiceType.objects.all():
        service_quotas[st.catalog_name] = []
        for z in st.zones.all():
            for r in models.Resource.objects.filter(service_type=st,
                                                    requestable=True):
                key = "%s_%s_%s" % (st.catalog_name, z.name, r.quota_name)
                all_quota_specs[key] = quota_spec(st.catalog_name,
                                                  r.quota_name,
                                                  zone=z.name)
    # Override with supplied quota specs
    for qs in quota_specs:
        key = "%s_%s_%s" % (qs['service'], qs['zone'], qs['resource'])
        all_quota_specs[key] = qs
    for qs in all_quota_specs.values():
        st = models.ServiceType.objects.get(catalog_name=qs['service'])
        r = models.Resource.objects.get(quota_name=qs['resource'],
                                                   service_type=st)
        service_quotas[st.catalog_name].append(
            {'id': '',
             'requested_quota': qs['requested_quota'],
             'quota': qs['quota'],
             'resource': r.id,
             'zone': qs['zone'],
             'group': ''})
    for service, quotas in service_quotas.items():
        group_list = []
        for zone in set(map(lambda q: q['zone'], quotas)):
            group_quotas = [q for q in quotas if q['zone'] == zone]
            if len(group_quotas) > 0:
                group_list.append({'id': '',
                                   'zone': zone,
                                   'service_type': service,
                                   'quotas': group_quotas})
        groups[service] = group_list
    return groups


def quota_spec(service, resource, quota=0, requested_quota=0, zone='nectar'):
    return {'service': service,
            'resource': resource,
            'quota': quota,
            'requested_quota': requested_quota,
            'zone': zone}


def add_quota_forms(form, all_quotas, service_type, group_list,
                    prefix_start='a'):
    new_prefix = prefix_start
    for group in group_list:
        if group['id']:
            prefix = group['id']
        else:
            prefix = new_prefix
            new_prefix = next_char(new_prefix)

        quotas = group.pop('quotas')
        form['%s_%s-INITIAL_FORMS' %
             (service_type, prefix)] = len(quotas) if group['id'] else 0
        resource_count = models.Resource.objects.filter(
            service_type__catalog_name=service_type,
            requestable=True).count()
        form['%s_%s-TOTAL_FORMS' % (service_type, prefix)] = resource_count
        form['%s_%s-MAX_NUM_FORMS' % (service_type, prefix)] = 1000

        for i, quota in enumerate(quotas):
            all_quotas.append({'resource': quota['resource'],
                               'zone': group['zone'],
                               'requested_quota': quota['requested_quota'],
                               'quota': quota['quota']})
            for k, v in quota.items():
                form['%s_%s-%s-%s' % (service_type, prefix, i, k)] = v

        for k, v in group.items():
            form['%s_%s-%s' % (service_type, prefix, k)] = v


def next_char(c):
    return chr(ord(c) + 1)


def request_allocation(user, model=None, quota_specs=None,
                       supported_organisations=None,
                       institutions=None, publications=None, grants=None,
                       usage_types=None, investigators=None):
    duration = fuzzy.FuzzyChoice(DURATION_CHOICES.keys()).fuzz()
    forp_1 = fuzzy.FuzzyInteger(1, 8).fuzz()
    forp_2 = fuzzy.FuzzyInteger(1, 9 - forp_1).fuzz()
    forp_3 = 10 - (forp_1 + forp_2)
    for_code = fuzzy.FuzzyChoice(
        forcodes.FOR_CODES[forcodes.FOR_SERIES].keys())
    quota = fuzzy.FuzzyInteger(1, 100000)
    site = model.associated_site if model else None

    model_dict = {'project_name': fuzzy.FuzzyText().fuzz(),
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
                  'estimated_number_users': quota.fuzz(),
                  'geographic_requirements': fuzzy.FuzzyText().fuzz(),
                  'associated_site': site,
                  }

    if model:
        groups = {}
        for name in GROUP_NAMES:
            groups[name] = get_groups(name, model)

        institutions = [{'id': ins.id,
                         'name': ins.name}
                        for ins in model.institutions.all()]

        publications = [{'id': pub.id,
                         'publication': pub.publication,
                         'output_type': pub.output_type,
                         'doi': pub.doi,
                         'crossref_metadata': pub.crossref_metadata
                        }
                        for pub in model.publications.all()]

        grants = [{'id': grant.id,
                   'grant_type': 'arc',
                   'grant_subtype': 'arc-discovery',
                   'funding_body_scheme': grant.funding_body_scheme,
                   'grant_id': grant.grant_id,
                   'first_year_funded': 2015,
                   'last_year_funded': 2017,
                   'total_funding': quota.fuzz(),
                  }
                  for grant in model.grants.all()]

        investigators = [{'id': inv.id,
                          'title': inv.title,
                          'given_name': inv.given_name,
                          'surname': inv.surname,
                          'email': inv.email,
                          'institution': inv.institution,
                          'primary_organisation': inv.primary_organisation,
                          'additional_researchers': inv.additional_researchers
                         }
                         for inv in model.investigators.all()]

        usage_types = model.usage_types.all()

        supported_organisations = model.supported_organisations.all()

    else:
        if quota_specs is None:
            groups = {}
            for name in GROUP_NAMES:
                groups[name] = get_groups(name)
        else:
            groups = quota_specs_to_groups(quota_specs)

        if institutions is None:
            institutions = [
                {'id': '',
                 'name': 'Monash University'}]

        if publications is None:
            publications = [
                {'id': '',
                 'publication': 'publication testing',
                 'output_type': 'AN',
                 'doi': '',
                 'crossref_metadata': ''}]

        if grants is None:
            grants = [{
                'id': '',
                'grant_type': 'arc',
                'grant_subtype': 'arc-discovery',
                'funding_body_scheme': 'ARC funding scheme',
                'grant_id': 'arc-grant-0001',
                'first_year_funded': 2015,
                'last_year_funded': 2017,
                'total_funding': quota.fuzz()
            }]

        if investigators is None:
            investigators = [{
                'id': '',
                'title': 'Prof.',
                'given_name': 'MeRC',
                'surname': 'Monash',
                'email': 'merc.monash@monash.edu',
                'institution': 'Monash University',
                'primary_organisation':
                    models.Organisation.objects.get(short_name='Monash'),
                'additional_researchers': 'None'
            }]

        if usage_types is None:
            usage_types = factories.get_active_usage_types()

        if supported_organisations is None:
            supported_organisations = [
                models.Organisation.objects.get(short_name='Monash')]

    form = model_dict.copy()
    all_quotas = []

    prefix_start = 'b' if model else 'a'
    for name, group_list in groups.items():
        add_quota_forms(form, all_quotas, name, group_list, prefix_start)

    form['institutions-INITIAL_FORMS'] = \
        model.institutions.count() if model else 0
    form['institutions-TOTAL_FORMS'] = len(institutions)
    form['institutions-MAX_NUM_FORMS'] = 1000

    form['publications-INITIAL_FORMS'] = \
        model.publications.count() if model else 0
    form['publications-TOTAL_FORMS'] = len(publications)
    form['publications-MAX_NUM_FORMS'] = 1000

    form['grants-INITIAL_FORMS'] = model.grants.count() if model else 0
    form['grants-TOTAL_FORMS'] = len(grants)
    form['grants-MAX_NUM_FORMS'] = 1000

    form['investigators-INITIAL_FORMS'] = \
        model.investigators.count() if model else 0
    form['investigators-TOTAL_FORMS'] = len(investigators)
    form['investigators-MAX_NUM_FORMS'] = 1000

    for i, ins in enumerate(institutions):
        for k, v in ins.items():
            form['institutions-%s-%s' % (i, k)] = v

    for i, pub in enumerate(publications):
        for k, v in pub.items():
            form['publications-%s-%s' % (i, k)] = v

    for i, grant in enumerate(grants):
        for k, v in grant.items():
            form['grants-%s-%s' % (i, k)] = v

    for i, inv in enumerate(investigators):
        for k, v in inv.items():
            form['investigators-%s-%s' % (i, k)] = (
                v.id if k == 'primary_organisation' else v)

    form['usage_types'] = [usage.name for usage in usage_types]
    form['supported_organisations'] = ','.join([
        str(org.id) for org in supported_organisations])
    form['associated_site'] = site or ''
    model_dict['quotas'] = all_quotas
    model_dict['institutions'] = institutions
    model_dict['supported_organisations'] = supported_organisations
    model_dict['publications'] = publications
    model_dict['grants'] = grants
    model_dict['investigators'] = investigators
    model_dict['usage_types'] = usage_types
    return model_dict, form
