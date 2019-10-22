import logging

from django.conf import settings

from nectar_dashboard.rcallocation import models


LOG = logging.getLogger('nectar_dashboard.rcallocation')

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
MANILA_NOT_LOCAL = 'MANILA_NOT_LOCAL'
NO_ROUTER = 'NO_ROUTER'
NO_NETWORK = 'NO_NETWORK'
FLOATING_IP_DEP = 'FLOATING_IP_DEP'
LOAD_BALANCER_DEP = 'LOAD_BALANCER_DEP'
APPROVER_PROBLEM = 'APPROVER_PROBLEM'
APPROVER_NOT_AUTHORIZED = 'APPROVER_NOT_AUTHORIZED'


def storage_zone_to_home(zone):
    for home, zones in settings.ALLOCATION_HOME_STORAGE_ZONE_MAPPINGS.items():
        if zone in zones:
            return home
    return None


def instance_vcpu_check(context):
    cores = context.get('compute.cores')
    instances = context.get('compute.instances')
    if cores < instances:
        return (INSTANCE_VCPU,
                "requested instances (%d) > requested VCPUs (%d)" %
                (instances, cores))
    else:
        return None


def no_vcpu_check(context):
    if context.get('compute.cores') == 0:
        return (NO_VCPU, "no VCPUs requested")
    else:
        return None


def no_instance_check(context):
    if context.get('compute.instances') == 0:
        return (NO_INSTANCE, "no instances requested")
    else:
        return None


def nondefault_ram_check(context):
    vcpus = context.get('compute.cores')
    mem = context.get('compute.ram')
    if vcpus > 0 and mem > 0:
        if vcpus * 4 < mem:
            return (LARGE_MEM,
                    "non-default RAM (%d GB) > 4GB per core ratio" % mem)
        elif vcpus * 4 > mem:
            return (SMALL_MEM,
                    "non-default RAM (%d GB) < 4GB per core ratio" % mem)
    return None


def cinder_instance_check(context):
    if context.get('compute.instances') == 0:
        for q in context.get_all('volume.gigabytes'):
            if q['value'] > 0:
                return (CINDER_WITHOUT_INSTANCES,
                        'volume storage requested without any instances')
    return None


def cinder_local_check(context):
    associated_site = context.get_field('associated_site')
    if associated_site:
        for q in context.get_all('volume.gigabytes'):
            if q['value'] <= 0:
                continue
            zone_home = storage_zone_to_home(q['zone'])
            if zone_home and zone_home != associated_site.name:
                return (CINDER_NOT_LOCAL,
                        '%s-local allocation requests volume storage in %s'
                        % (associated_site.name, q['zone']))
    return None


def manila_local_check(context):
    associated_site = context.get_field('associated_site')
    if associated_site:
        for q in context.get_all('share.shares'):
            if q['value'] <= 0:
                continue
            zone_home = storage_zone_to_home(q['zone'])
            if zone_home and zone_home != associated_site.name:
                return (MANILA_NOT_LOCAL,
                        '%s-local allocation requests shares in %s'
                        % (associated_site.name, q['zone']))
    return None


def neutron_checks(context):
    ips = context.get('network.floatingip')
    networks = context.get('network.network')
    routers = context.get('network.router')
    loadbalancers = context.get('network.loadbalancer')
    if ips > 0 and (networks == 0 or routers == 0):
        return (FLOATING_IP_DEP,
                'floating ips require at least 1 network and 1 router')
    if loadbalancers > 0 and (networks == 0 or routers == 0):
        return (LOAD_BALANCER_DEP,
                'load balancers require at least 1 network and 1 router')
    if networks > 0 and routers == 0:
        return (NO_ROUTER,
                'use of advanced networks requires at least 1 router')
    if networks == 0 and routers > 0:
        return (NO_NETWORK,
                'use of advanced networks requires at least 1 network')


def approver_checks(context):
    if context.user is None or not context.approving:
        return
    username = context.user.username
    try:
        approver = models.Approver.objects.get(username=username)
    except models.Approver.DoesNotExist:
        LOG.warning("No Approver object found for '%s'", username)
        return (APPROVER_PROBLEM,
                'problem with approver registration: contact Core Services')
    sites = approver.sites.all()
    if len(sites) == 0:
        LOG.warning("Approver object for '%s' has no associated sites",
                    username)
        return (APPROVER_PROBLEM,
                'problem with approver registration: contact Core Services')

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
             """quota should be authorized by the other site before
             approving '%s' storage quota""" % z) for z in other_zones]


STD_CHECKS = [instance_vcpu_check,
              no_vcpu_check,
              no_instance_check,
              nondefault_ram_check,
              cinder_instance_check,
              cinder_local_check,
              manila_local_check,
              neutron_checks,
              approver_checks]


class QuotaSanityContext(object):

    def __init__(self, form=None, requested=True, user=None,
                 quotas=[], approving=False, checks=STD_CHECKS,
                 allocation=None):
        self.all_quotas = {}
        self._do_add(quotas)
        self.checks = checks
        self.requested = requested
        self.form = form
        self.user = user
        self.approving = approving
        self.allocation = allocation

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

    def get(self, quota_name, zone='nectar'):
        quotas = [q for q in self.all_quotas.values()
                  if q['name'] == quota_name and q['zone'] == zone]
        if len(quotas) >= 1:
            return quotas[0]['value']
        else:
            return 0

    def get_all(self, quota_name):
        return [q for q in self.all_quotas.values()
                if q['name'] == quota_name and q['value'] > 0]

    def get_field(self, name):
        value = self.form.cleaned_data.get(name)
        if value is None and self.allocation:
            value = getattr(self.allocation, name, None)
        return value
