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
                "Requested instances (%d) > requested VCPUs (%d)" %
                (instances, cores))
    else:
        return None


def no_vcpu_check(context):
    if context.get('compute.cores') == 0:
        return (NO_VCPU, "No VCPUs requested")
    else:
        return None


def no_instance_check(context):
    if context.get('compute.instances') == 0:
        return (NO_INSTANCE, "No instances requested")
    else:
        return None


def nondefault_ram_check(context):
    vcpus = context.get('compute.cores')
    mem = context.get('compute.ram')
    if vcpus > 0 and mem > 0:
        if vcpus * 4 < mem:
            return (LARGE_MEM,
                    "Non-default RAM (%d GB) > 4GB per core ratio" % mem)
        elif vcpus * 4 > mem:
            return (SMALL_MEM,
                    "Non-default RAM (%d GB) < 4GB per core ratio" % mem)
    return None


def cinder_instance_check(context):
    if context.get('compute.instances') == 0:
        for q in context.get_all('volume.gigabytes'):
            if q['value'] > 0:
                return (CINDER_WITHOUT_INSTANCES,
                        'Volume storage requested without any instances')
    return None


def cinder_local_check(context):
    associated_site = context.get_field('associated_site')
    if associated_site:
        for q in context.get_all('volume.gigabytes'):
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
    if context.get('database.ram') > 0 \
       and context.get('database.volumes') == 0:
        return (TROVE_WITHOUT_STORAGE,
                'Database RAM requested without any database storage')
    return None


def trove_ram_check(context):
    ram = context.get('database.ram')
    if ram == 0 \
       and context.get('database.volumes') > 0:
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
    if (context.get('database.ram') > 0
        or context.get('database.volumes') > 0) \
       and context.get('object.object') == 0:
        return (TROVE_WITHOUT_SWIFT,
                "No object storage quota requested. This is required if you"
                " want to use the database service backup functionality")
    return None


def magnum_instance_check(context):
    clusters = context.get('container-infra.cluster')
    if clusters * 2 > context.get('compute.instances'):
        return (CLUSTER_WITHOUT_INSTANCES,
                'At least %s instances advised for %s clusters'
                % (clusters * 2, clusters))


def magnum_neutron_checks(context):
    clusters = context.get('container-infra.cluster')
    if clusters > context.get('network.network'):
        return (CLUSTER_WITHOUT_NETWORK,
                '%s networks advised for %s clusters'
                % (clusters, clusters))
    if clusters * 3 > context.get('network.loadbalancer'):
        return (CLUSTER_WITHOUT_LBS,
                '%s load balancers advised for %s clusters'
                % (clusters * 3, clusters))
    if clusters * 2 > context.get('network.floatingip'):
        return (CLUSTER_WITHOUT_FIPS,
                '%s floating ips advised for %s clusters'
                % (clusters * 2, clusters))
    if clusters > context.get('network.router'):
        return (CLUSTER_WITHOUT_ROUTER,
                '%s routers advised for %s clusters'
                % (clusters * 2, clusters))


def manila_local_check(context):
    associated_site = context.get_field('associated_site')
    if associated_site:
        for q in context.get_all('share.shares'):
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
    ips = context.get('network.floatingip')
    networks = context.get('network.network')
    routers = context.get('network.router')
    loadbalancers = context.get('network.loadbalancer')
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


def approver_checks(context):
    if context.user is None or not context.approving:
        return
    username = context.user.username
    try:
        approver = models.Approver.objects.get(username=username)
    except models.Approver.DoesNotExist:
        LOG.warning("No Approver object found for '%s'", username)
        return (APPROVER_PROBLEM,
                'Problem with approver registration: contact Core Services')
    sites = approver.sites.all()
    if len(sites) == 0:
        LOG.warning("Approver object for '%s' has no associated sites",
                    username)
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


STD_CHECKS = [instance_vcpu_check,
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
