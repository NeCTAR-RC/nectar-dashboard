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
INSTANCE_VCPU = 'INSTANCE_VCPU'
NO_VCPU = 'NO_VCPU'
NO_INSTANCE = 'NO_INSTANCE'
LARGE_MEM = 'LARGE_MEM'
SMALL_MEM = 'SMALL_MEM'
CINDER_WITHOUT_INSTANCES = 'CINDER_WITHOUT_INSTANCES'
CINDER_NOT_LOCAL = 'CINDER_NOT_LOCAL'
TROVE_WITHOUT_STORAGE = 'TROVE_WITHOUT_STORAGE'
TROVE_WITHOUT_RAM = 'TROVE_WITHOUT_RAM'
TROVE_WITHOUT_SWIFT = 'TROVE_WITHOUT_SWIFT'
MANILA_NOT_LOCAL = 'MANILA_NOT_LOCAL'
NO_ROUTER = 'NO_ROUTER'
NO_NETWORK = 'NO_NETWORK'
FLOATING_IP_DEP = 'FLOATING_IP_DEP'
LOAD_BALANCER_DEP = 'LOAD_BALANCER_DEP'
CLUSTER_WITHOUT_INSTANCES = 'CLUSTER_WITHOUT_INSTANCES'
CLUSTER_WITHOUT_NETWORK = 'CLUSTER_WITHOUT_NETWORK'
CLUSTER_WITHOUT_LBS = 'CLUSTER_WITHOUT_LBS'
CLUSTER_WITHOUT_FIPS = 'CLUSTER_WITHOUT_FIPS'
CLUSTER_WITHOUT_ROUTER = 'CLUSTER_WITHOUT_ROUTER'
FLAVORS_NOT_JUSTIFIED = 'FLAVORS_NOT_JUSTIFIED'
APPROVER_PROBLEM = 'APPROVER_PROBLEM'
APPROVER_NOT_AUTHORIZED = 'APPROVER_NOT_AUTHORIZED'
NO_VALID_GRANTS = 'NO_VALID_GRANTS'
NO_BUDGET = 'NO_BUDGET'
ZERO_RESERVATIONS = 'ZERO_RESERVATIONS'
ZERO_DURATION = 'ZERO_DURATION'
REENTER_FOR_CODES = 'REENTER_FOR_CODES'


def storage_zone_to_home(zone):
    for home, zones in settings.ALLOCATION_HOME_STORAGE_ZONE_MAPPINGS.items():
        if zone in zones:
            return home
    return None


def no_budget_check(context):
    budget = context.get_quota('rating.budget')
    if budget <= 0:
        return (NO_BUDGET,
                'No Service Unit Budget has been entered')
    return None


def instance_vcpu_check(context):
    cores = context.get_quota('compute.cores')
    instances = context.get_quota('compute.instances')
    if cores < instances:
        return (INSTANCE_VCPU,
                "Requested instances (%d) > requested VCPUs (%d)" %
                (instances, cores))
    else:
        return None


def no_vcpu_check(context):
    if context.get_quota('compute.cores') == 0:
        return (NO_VCPU, "No VCPUs requested")
    else:
        return None


def no_instance_check(context):
    if context.get_quota('compute.instances') == 0:
        return (NO_INSTANCE, "No instances requested")
    else:
        return None


def nondefault_ram_check(context):
    vcpus = context.get_quota('compute.cores')
    mem = context.get_quota('compute.ram')
    if vcpus > 0 and mem > 0:
        if vcpus * 4 < mem:
            return (LARGE_MEM,
                    "Non-default RAM (%d GB) > 4GB per core ratio" % mem)
        elif vcpus * 4 > mem:
            return (SMALL_MEM,
                    "Non-default RAM (%d GB) < 4GB per core ratio" % mem)
    return None


def cinder_instance_check(context):
    if context.get_quota('compute.instances') == 0:
        for q in context.get_all_quotas('volume.gigabytes'):
            if q['value'] > 0:
                return (CINDER_WITHOUT_INSTANCES,
                        'Volume storage requested without any instances')
    return None


def cinder_local_check(context):
    associated_site = context.get_field('associated_site')
    if associated_site:
        for q in context.get_all_quotas('volume.gigabytes'):
            if q['value'] <= 0:
                continue
            zone_home = storage_zone_to_home(q['zone'])
            if zone_home and zone_home != associated_site.name:
                national = context.get_field('national')
                return (CINDER_NOT_LOCAL,
                        '%s approved %s allocation requests volume storage '
                        'in %s'
                        % (associated_site.name,
                           'national' if national else 'local',
                           q['zone']))
    return None


def trove_storage_check(context):
    if context.get_quota('database.ram') > 0 \
       and context.get_quota('database.volumes') == 0:
        return (TROVE_WITHOUT_STORAGE,
                'Database RAM requested without any database storage')
    return None


def trove_ram_check(context):
    ram = context.get_quota('database.ram')
    if ram == 0 \
       and context.get_quota('database.volumes') > 0:
        return (TROVE_WITHOUT_RAM,
                'Database storage requested without any database RAM')
    elif ram > 0:
        if ram < 4:
            return ('', "Database RAM should be at least 4GB")
        elif ram > 100:
            return ('', "Database RAM  max limit is 100GB")
        elif ram % 4 != 0:
            return ('',
                    "Database RAM should be a multiple of 4")
    return None


def trove_backup_check(context):
    if (context.get_quota('database.ram') > 0
        or context.get_quota('database.volumes') > 0) \
       and context.get_quota('object.object') == 0:
        return (TROVE_WITHOUT_SWIFT,
                "No object storage quota requested. This is required if you"
                " want to use the database service backup functionality")
    return None


def magnum_instance_check(context):
    clusters = context.get_quota('container-infra.cluster')
    if clusters * 2 > context.get_quota('compute.instances'):
        return (CLUSTER_WITHOUT_INSTANCES,
                'At least %s instances advised for %s clusters'
                % (clusters * 2, clusters))
    return None


def magnum_neutron_checks(context):
    clusters = context.get_quota('container-infra.cluster')
    if clusters > context.get_quota('network.network'):
        return (CLUSTER_WITHOUT_NETWORK,
                '%s networks advised for %s clusters'
                % (clusters, clusters))
    if clusters * 3 > context.get_quota('network.loadbalancer'):
        return (CLUSTER_WITHOUT_LBS,
                '%s load balancers advised for %s clusters'
                % (clusters * 3, clusters))
    if clusters * 2 > context.get_quota('network.floatingip'):
        return (CLUSTER_WITHOUT_FIPS,
                '%s floating ips advised for %s clusters'
                % (clusters * 2, clusters))
    if clusters > context.get_quota('network.router'):
        return (CLUSTER_WITHOUT_ROUTER,
                '%s routers advised for %s clusters'
                % (clusters * 2, clusters))
    return None


def manila_local_check(context):
    associated_site = context.get_field('associated_site')
    if associated_site:
        for q in context.get_all_quotas('share.shares'):
            if q['value'] <= 0:
                continue
            zone_home = storage_zone_to_home(q['zone'])
            if zone_home and zone_home != associated_site.name:
                national = context.get_field('national')
                return (MANILA_NOT_LOCAL,
                        '%s approved %s allocation requests shares in %s'
                        % (associated_site.name,
                           'national' if national else 'local',
                           q['zone']))
    return None


def neutron_checks(context):
    ips = context.get_quota('network.floatingip')
    networks = context.get_quota('network.network')
    routers = context.get_quota('network.router')
    loadbalancers = context.get_quota('network.loadbalancer')
    if ips > 0 and (networks == 0 or routers == 0):
        return (FLOATING_IP_DEP,
                'Floating ips require at least 1 network and 1 router')
    if loadbalancers > 0 and (networks == 0 or routers == 0):
        return (LOAD_BALANCER_DEP,
                'Load balancers require at least 1 network and 1 router')
    if networks > 0 and routers == 0:
        return (NO_ROUTER,
                'Use of advanced networks requires at least 1 router')
    if networks == 0 and routers > 0:
        return (NO_NETWORK,
                'Use of advanced networks requires at least 1 network')
    return None


def flavor_check(context):
    huge_ram = context.get_quota('compute.flavor:hugeram-v3')
    if huge_ram and not context.get_field('usage_patterns'):
        return (FLAVORS_NOT_JUSTIFIED,
                'Requests for access to special flavors must be explained '
                'in the "Justification ..." field.')
    return None


def reservation_check(context):
    days = context.get_quota('nectar-reservation.days')
    reservations = context.get_quota('nectar-reservation.reservations')
    gpu = context.get_quota('nectar-reservation.flavor:GPU')
    huge = context.get_quota('nectar-reservation.flavor:Huge RAM')
    if not reservations and not days and not gpu and not huge:
        return None

    res = []
    if days == 0:
        res.append((ZERO_DURATION,
                    'The combined reservation duration should be > 0'))
    if reservations == 0:
        res.append((ZERO_RESERVATIONS,
                    'The number of reservations should be > 0'))
    return res


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
    for q in context.all_quotas.values():
        if q['value'] > 0 and q['zone'] != 'nectar':
            if not q['zone'] in approver_zones:
                other_zones.add(q['zone'])

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


STD_CHECKS = [no_budget_check,
              instance_vcpu_check,
              no_vcpu_check,
              no_instance_check,
              nondefault_ram_check,
              cinder_instance_check,
              cinder_local_check,
              trove_storage_check,
              trove_ram_check,
              trove_backup_check,
              manila_local_check,
              neutron_checks,
              magnum_instance_check,
              magnum_neutron_checks,
              flavor_check,
              approver_checks,
              grant_checks,
              reservation_check,
]


class Checker(object):

    def __init__(self, form=None, user=None,
                 checks=STD_CHECKS, allocation=None):
        self.checks = checks
        self.form = form
        self.user = user
        self.allocation = allocation

    def do_checks(self):
        res = []
        for check in self.checks:
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
                 quotas=[], approving=False, checks=STD_CHECKS,
                 allocation=None):
        super().__init__(form=form, user=user, checks=checks,
                         allocation=allocation)
        self.all_quotas = {}
        self._do_add(quotas)
        self.requested = requested
        self.approving = approving

    def add_quotas(self, quotas_to_check):
        self._do_add(self._convert_quotas(quotas_to_check))

    def _do_add(self, quotas):
        for q in quotas:
            self.all_quotas[q['key']] = q

    def _convert_quotas(self, quotas_to_check):
        quotas = []
        for q in quotas_to_check:
            value = q.requested_quota \
                    if self.requested else q.quota
            name = "%s.%s" % (
                q.resource.service_type.catalog_name,
                q.resource.quota_name)
            key = "%s.%s.%s" % (
                q.resource.service_type.catalog_name,
                q.resource.quota_name,
                q.group.zone.name)
            quotas.append({'key': key,
                           'quota': q,
                           'value': value,
                           'name': name,
                           'zone': q.group.zone.name})
        return quotas

    def get_quota(self, quota_name, zone='nectar'):
        quotas = [q for q in self.all_quotas.values()
                  if q['name'] == quota_name and q['zone'] == zone]
        if len(quotas) >= 1:
            return quotas[0]['value']
        else:
            return 0

    def get_all_quotas(self, quota_name):
        return [q for q in self.all_quotas.values()
                if q['name'] == quota_name and q['value'] > 0]


ADD_BUDGET = 'ADD_BUDGET'
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


def new_budget_check(context):
    budget = context.get_quota('rating.budget')
    if budget <= 0:
        return (ADD_BUDGET,
                'Your allocation needs to change to use a Service Unit '
                'Budget. You need to estimate how many Service Units (SUs) '
                'your project needs for the next period.')
    return None


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


NAG_CHECKS = [new_budget_check, survey_check, ncris_check, ardc_check,
              grant_check, output_checks, for_check]


class NagChecker(Checker):

    def __init__(self, user=None, checks=NAG_CHECKS, allocation=None):
        super().__init__(form=None, user=user,
                         checks=checks, allocation=allocation)

    def get_quota(self, quota_name, zone='nectar', requested=False):
        '''Fetch the quota value from the allocation object.'''

        if self.allocation is None:
            return 0
        service_name, resource_name = quota_name.split('.')
        try:
            resource = models.Resource.objects.get(
                service_type__catalog_name=service_name,
                quota_name=resource_name)
        except models.Resource.DoesNotExist:
            # Either the ServiceType or Resource could be missing or have
            # the wrong catalog names ...
            raise RuntimeError(
                f"Can't get quota: Resource for ('{service_name}', "
                f"'{resource_name}') not found.")
        try:
            quota = models.Quota.objects.get(
                group__allocation=self.allocation.pk,
                resource=resource, group__zone__name=zone)
            return quota.requested_quota if requested else quota.quota
        except models.Quota.DoesNotExist:
            # This is an "expected" condition when an existing allocation
            # record doesn't have a QuotaGroup or Quota object for the
            # given quota name.
            return 0
