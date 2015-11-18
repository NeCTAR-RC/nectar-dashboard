from datetime import date, timedelta
from django.forms.models import model_to_dict
from factory import fuzzy

from rcportal.rcallocation import for_choices, project_duration_choices, \
    allocation_home_choices, grant_type

FOR_CHOICES = dict(for_choices.FOR_CHOICES)
DURATION_CHOICES = dict(project_duration_choices.DURATION_CHOICE)
ALLOCATION_HOMES = dict(allocation_home_choices.ALLOC_HOME_CHOICE)
GRANT_TYPES = dict(grant_type.GRANT_TYPES)


def allocation_to_dict(model):
    allocation = model_to_dict(model)
    allocation['quota'] = [model_to_dict(quota)
                           for quota in model.quotas.all()]

    allocation['institution'] = [model_to_dict(institution)
                                 for institution in model.institutions.all()]

    allocation['publication'] = [model_to_dict(publication)
                                 for publication in model.publications.all()]

    allocation['grant'] = [model_to_dict(grant)
                           for grant in model.grants.all()]

    allocation['investigator'] = [model_to_dict(inv)
                                  for inv in model.investigators.all()]
    return allocation


def request_allocation(user, model=None, quotas=None, institutions=None,
                       publications=None, grants=None, investigators=None):
    _1_year = date.today() + timedelta(days=365)
    start_date = fuzzy.FuzzyDate(date.today(), _1_year).fuzz()
    duration = fuzzy.FuzzyChoice(DURATION_CHOICES.keys()).fuzz()
    forp_1 = fuzzy.FuzzyInteger(1, 8).fuzz()
    forp_2 = fuzzy.FuzzyInteger(1, 9 - forp_1).fuzz()
    forp_3 = 10 - (forp_1 + forp_2)
    for_code = fuzzy.FuzzyChoice(FOR_CHOICES.keys())
    quota = fuzzy.FuzzyInteger(1, 100000)
    alloc_home = fuzzy.FuzzyChoice(ALLOCATION_HOMES.keys())
    grant_type = fuzzy.FuzzyChoice(GRANT_TYPES.keys())

    model_dict = {'tenant_name': fuzzy.FuzzyText().fuzz(),
                  'project_name': fuzzy.FuzzyText().fuzz(),
                  'start_date': start_date,  # only used for asserting
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
                  'allocation_home': alloc_home.fuzz(),
                  'core_hours': quota.fuzz(),
                  'primary_instance_type': ' ',
                  'cores': quota.fuzz(),
                  'instances': quota.fuzz(),
                  'nectar_support': 'nectar supporting',
                  'ncris_support': 'ncris supporting',
                  }

    if model:
        quotas = [{'id': q.id,
                   'requested_quota': quota.fuzz(),
                   'resource': q.resource,
                   'quota': 0,
                   'zone': q.zone}
                  for q in model.quotas.all()]

        institutions = [{'id': ins.id,
                         'name': ins.name}
                        for ins in model.institutions.all()]

        publications = [{'id': pub.id,
                         'publication': pub.publication}
                        for pub in model.publications.all()]

        grants = [{'id': grant.id,
                   'grant_type': grant_type.fuzz(),
                   'funding_body': grant.funding_body,
                   'scheme': grant.scheme,
                   'grant_id': grant.grant_id,
                   'first_year_funded': 2015,
                   'total_funding': quota.fuzz()
                   }
                  for grant in model.grants.all()]

        investigators = [{'id': inv.id,
                          'title': inv.title,
                          'given_name': inv.given_name,
                          'surname': inv.surname,
                          'email': inv.email,
                          'institution': inv.institution,
                          'additional_researchers': inv.additional_researchers
                          }
                         for inv in model.investigators.all()]

    else:
        if not quotas:
            quotas = [
                {'id': '',
                 'requested_quota': quota.fuzz(),
                 'resource': 'object',
                 'quota': 0,
                 'zone': 'nectar'},
                {'id': '',
                 'requested_quota': quota.fuzz(),
                 'resource': 'volume',
                 'quota': 0,
                 'zone': 'melbourne'},
                {'id': '',
                 'requested_quota': quota.fuzz(),
                 'resource': 'volume',
                 'quota': 0,
                 'zone': 'monash'}]

        if not institutions:
            institutions = [
                {'id': '',
                 'name': 'Monash'}]

        if not publications:
            publications = [
                {'id': '',
                 'publication': 'publication testing'}]

        if not grants:
            grants = [{
                'id': '',
                'grant_type': grant_type.fuzz(),
                'funding_body': 'ARC funding',
                'scheme': 'ARC scheme',
                'grant_id': 'arc-grant-0001',
                'first_year_funded': 2015,
                'total_funding': quota.fuzz()
            }]

        if not investigators:
            investigators = [{
                'id': '',
                'title': 'Prof.',
                'given_name': 'MeRC',
                'surname': 'Monash',
                'email': 'merc.monash@monash.edu',
                'institution': 'Monash University',
                'additional_researchers': 'None'
            }]

    form = model_dict.copy()
    form['quotas-INITIAL_FORMS'] = model.quotas.count() if model else 0
    form['quotas-TOTAL_FORMS'] = len(quotas)
    form['quotas-MAX_NUM_FORMS'] = 1000

    form['institutions-INITIAL_FORMS'] = model.institutions.count() \
        if model else 0
    form['institutions-TOTAL_FORMS'] = len(institutions)
    form['institutions-MAX_NUM_FORMS'] = 1000

    form['publications-INITIAL_FORMS'] = model.publications.count() \
        if model else 0
    form['publications-TOTAL_FORMS'] = len(publications)
    form['publications-MAX_NUM_FORMS'] = 1000

    form['grants-INITIAL_FORMS'] = model.grants.count() if model else 0
    form['grants-TOTAL_FORMS'] = len(grants)
    form['grants-MAX_NUM_FORMS'] = 1000

    form['investigators-INITIAL_FORMS'] = model.investigators.count() \
        if model else 0
    form['investigators-TOTAL_FORMS'] = len(investigators)
    form['investigators-MAX_NUM_FORMS'] = 1000

    for i, quota in enumerate(quotas):
        for k, v in quota.items():
            form['quotas-%s-%s' % (i, k)] = v

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
            form['investigators-%s-%s' % (i, k)] = v

    model_dict['quotas'] = quotas
    model_dict['institutions'] = institutions
    model_dict['publications'] = publications
    model_dict['grants'] = grants
    model_dict['investigators'] = investigators
    return model_dict, form
