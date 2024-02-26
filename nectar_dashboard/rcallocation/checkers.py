# Copyright 2021 Australian Research Data Commons
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from datetime import datetime
import logging

from django.conf import settings

from nectar_dashboard.rcallocation import forcodes
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import output_type_choices


LOG = logging.getLogger('nectar_dashboard.rcallocation')

FOR_CODES = forcodes.FOR_CODES[forcodes.FOR_SERIES]


# The following warning code strings will used as anchors in the
# support page that contains "more information" about the errors.
# The values should be stable and unique.
CINDER_NOT_LOCAL = 'CINDER_NOT_LOCAL'
MANILA_NOT_LOCAL = 'MANILA_NOT_LOCAL'
FLAVORS_NOT_JUSTIFIED = 'FLAVORS_NOT_JUSTIFIED'
APPROVER_PROBLEM = 'APPROVER_PROBLEM'
APPROVER_NOT_AUTHORIZED = 'APPROVER_NOT_AUTHORIZED'
APPROVER_DISABLED_ORGANISATION = 'APPROVER_DISABLED_ORGANISATION'
APPROVER_UNVETTED_ORGANISATION = 'APPROVER_UNVETTED_ORGANISATION'
NO_VALID_GRANTS = 'NO_VALID_GRANTS'
REENTER_FOR_CODES = 'REENTER_FOR_CODES'


def storage_zone_to_home(zone):
    for home, zones in settings.ALLOCATION_HOME_STORAGE_ZONE_MAPPINGS.items():
        if zone in zones:
            return home
    return None


def get_foreign_zones(associated_sites):
    zones = set([z.name for z in models.Zone.objects.all()])
    for site in associated_sites:
        home_zones = set(settings.ALLOCATION_HOME_STORAGE_ZONE_MAPPINGS.get(
            site.name, []))
        zones -= home_zones
    return zones


def cinder_local_check(context):
    associated_site = context.get_field('associated_site')
    if associated_site:
        foreign_zones = get_foreign_zones([associated_site])
        for zone in foreign_zones:
            q = context.get_field(f'quota-volume.gigabytes__{zone}')
            if not q or q == 0:
                continue
            national = context.get_field('national')
            return (CINDER_NOT_LOCAL,
                    '%s approved %s allocation requests volume storage '
                    'in %s'
                    % (associated_site.name,
                       'national' if national else 'local',
                       zone))
    return None


def manila_local_check(context):
    associated_site = context.get_field('associated_site')
    if associated_site:
        foreign_zones = get_foreign_zones([associated_site])
        for zone in foreign_zones:
            q = context.get_field(f'quota-share.shares__{zone}')
            if not q or q == 0:
                continue
            national = context.get_field('national')
            return (MANILA_NOT_LOCAL,
                    '%s approved %s allocation requests shares '
                    'in %s'
                    % (associated_site.name,
                       'national' if national else 'local',
                       zone))
    return None


def flavor_check(context):
    bundle = context.get_field('bundle')
    if bundle:
        return None
    huge_ram = context.get_field('quota-compute.flavor:hugeram-v3__nectar')
    if huge_ram and not context.get_field('usage_patterns'):
        return (FLAVORS_NOT_JUSTIFIED,
                'Requests for access to special flavors must be explained '
                'in the "Justification ..." field.')
    return None


def approver_checks(context):
    if context.user is None or not context.approving:
        return None
    sites = models.Site.objects.get_by_approver(context.user.username)
    if len(sites) == 0:
        return (APPROVER_PROBLEM,
                'Problem with approver registration: contact Core Services')

    mappings = settings.ALLOCATION_HOME_STORAGE_ZONE_MAPPINGS
    approver_zones = []
    for s in sites:
        approver_zones.extend(mappings.get(s.name, []))
    other_zones = set()
    foreign_zones = get_foreign_zones(sites)
    for zone in foreign_zones:
        for prefix in ['quota-volume.gigabytes__',
                       'quota-share.shares__']:
            q = context.get_field(f'{prefix}{zone}')
            if q and q > 0:
                other_zones.add(zone)

    return [(APPROVER_NOT_AUTHORIZED,
             """Quota should be authorized by the other site before
             approving '%s' storage quota""" % z) for z in other_zones]


def grant_checks(context):
    if not context.approving:
        # These are approver-only checks.  When we look at the form
        # submitted by the user, there is not enough context to know
        # if warnings about grants, etc are relevant.
        return None

    this_year = datetime.now().year
    if (not context.get_field('national')
        or context.get_field('special_approval')
        or context.allocation.ardc_support.get_queryset().count()
        or context.allocation.ncris_facilities.get_queryset().count()):
        return None
    for g in context.allocation.grants.get_queryset():
        if (g.grant_type in ('arc', 'nhmrc', 'comp', 'govt', 'rdc')
            and g.last_year_funded >= this_year):
            return None
    return [(NO_VALID_GRANTS,
             "There are no current competitive grants for this request. "
             "Either approve it as Local, or add a Special approval reason.")]


def organisation_checks(context):
    if not context.approving:
        # These are approver-only checks.
        return None

    res = []

    def _check(org):
        if not org.enabled:
            res.append((APPROVER_DISABLED_ORGANISATION,
                        "This allocation request is using an Organisation "
                        f"({org.full_name}) that has been disabled. Please"
                        "get the user to resubmit with another Organisation."))
        elif org.proposed_by and not org.vetted_by:
            res.append((APPROVER_UNVETTED_ORGANISATION,
                        "This allocation request is using an Organisation "
                        f"({org.full_name}) that has been proposed "
                        f"(by {org.proposed_by}) but not vetted. "
                        "Please get an Allocations Admin to vet it before "
                        "approving this request or amendment."))

    for o in context.allocation.supported_organisations.all():
        _check(o)
    for ci in context.allocation.investigators.all():
        _check(ci.primary_organisation)

    return res or None


class Checker(object):

    CHECKS = [cinder_local_check, manila_local_check, flavor_check,
        approver_checks, organisation_checks, grant_checks,
    ]

    def __init__(self, form=None, user=None,
                 allocation=None):
        self.form = form
        self.user = user
        self.allocation = allocation

    def do_checks(self):
        res = []
        for check in self.CHECKS:
            info = check(self)
            # A check may return a tuple or a list of tuples
            if info:
                if isinstance(info, list):
                    res.extend(info)
                else:
                    res.append(info)
        return res

    def get_field(self, name):
        value = self.form.cleaned_data.get(name) if self.form else None
        if value is None and self.allocation:
            value = getattr(self.allocation, name, None)
        return value


class QuotaSanityChecker(Checker):

    def __init__(self, form=None, requested=True, user=None,
                 quotas=[], approving=False,
                 allocation=None):
        super().__init__(form=form, user=user,
                         allocation=allocation)
        self.approving = approving


NO_SURVEY = 'NO_SURVEY'
LEGACY_NCRIS = 'LEGACY_NCRIS'
LEGACY_ARDC = 'LEGACY_ARDC'
EXPIRED_GRANT = 'EXPIRED_GRANT'
UNSPECIFIED_OUTPUT = 'UNSPECIFIED_OUTPUT'
NO_CROSSREF = 'NO_CROSSREF'

# Grants that have expired this number of years ago are no longer
# relevant to allocation decisions.  Allocations ctty consensus is
# that 4 years is about right.
EXPIRED_GRANT_CUTOFF_YEARS = 4


def survey_check(checker):
    if checker.get_field('usage_types').all().count() == 0:
        return (NO_SURVEY,
                'One or more "Usage Types" need to be selected.')
    return None


def ncris_check(checker):
    if (checker.get_field('ncris_support')
        and checker.get_field('ncris_facilities').all().count() == 0):
        return (LEGACY_NCRIS,
                'The information that you previously entered for '
                'NCRIS support text box needs to be reviewed and '
                'reentered in the NCRIS facilities and details fields.')
    return None


def ardc_check(checker):
    if (checker.get_field('nectar_support')
        and checker.get_field('ardc_support').all().count() == 0):
        return (LEGACY_ARDC,
                'The information that you previously entered for '
                'Nectar support text box needs to be reentered in the '
                'ARDC support and details fields.')
    return None


def grant_check(checker):
    cutoff = datetime.now().year - EXPIRED_GRANT_CUTOFF_YEARS
    if models.Grant.objects.filter(allocation=checker.allocation,
                                   last_year_funded__lt=(cutoff + 1)).count():
        return (EXPIRED_GRANT,
                'One or more of your listed research grants ended in %s or '
                'earlier. Old grants that are no longer relevant to '
                'allocation renewal assessment should be removed from the '
                'form.' % (cutoff))
    return None


def output_checks(checker):
    UNSPECIFIED = output_type_choices.UNSPECIFIED
    JOURNAL = output_type_choices.PEER_REVIEWED_JOURNAL_ARTICLE

    res = []
    if models.Publication.objects.filter(allocation=checker.allocation,
                                         output_type=UNSPECIFIED).count():
        res.append((UNSPECIFIED_OUTPUT,
                    'One or more of the Publications / Outputs listed on the '
                    'form needs to be reentered with a publication category '
                    'and (if available) a DOI.  When you have done this, '
                    'please delete the old entry.'))
    if models.Publication.objects.filter(allocation=checker.allocation,
                                         output_type=JOURNAL,
                                         crossref_metadata="").count():
        res.append((NO_CROSSREF,
                    'One or more of your Publications has been entered as a '
                    'peer-reviewed journal article, but it does not have a '
                    'validated DOI.  Please reenter it.'))
    return res


def for_check(checker):
    for for_code in [checker.allocation.field_of_research_1,
                     checker.allocation.field_of_research_2,
                     checker.allocation.field_of_research_3]:
        if for_code and for_code not in FOR_CODES.keys():
            return [(REENTER_FOR_CODES,
                     'This allocation request is using legacy Field of '
                     'Research (FoR) codes.  You will need to reenter the '
                     'FoR information using '
                     f'{forcodes.FOR_SERIES.replace("_", " ")} codes.')]


class NagChecker(Checker):
    CHECKS = [survey_check, ncris_check, ardc_check,
              grant_check, output_checks, for_check]
