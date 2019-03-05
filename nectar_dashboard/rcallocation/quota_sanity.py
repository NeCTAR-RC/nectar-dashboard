import logging


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
NO_ROUTER = 'NO_ROUTER'
NO_NETWORK = 'NO_NETWORK'
FLOATING_IP_DEP = 'FLOATING_IP_DEP'
LOAD_BALANCER_DEP = 'LOAD_BALANCER_DEP'


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
    mem = context.get('compute.memory')
    if vcpus > 0 and mem > 0:
        if vcpus * 4096 < mem:
            return (LARGE_MEM,
                    "non-default RAM (%d MB) > 4GB per core ratio" % mem)
        elif vcpus * 4096 > mem:
            return (SMALL_MEM,
                    "non-default RAM (%d MB) < 4GB per core ratio" % mem)
    return None


def cinder_without_instance_check(context):
    if context.get('compute.instances') == 0:
        for q in context.get_all('volume.gigabytes'):
            if q['value'] > 0:
                return (CINDER_WITHOUT_INSTANCES,
                        'volume storage requested without any instances')
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


STD_CHECKS = [instance_vcpu_check,
              no_vcpu_check,
              no_instance_check,
              nondefault_ram_check,
              cinder_without_instance_check,
              neutron_checks]


class QuotaSanityContext:

    def __init__(self, form, requested=True,
                 quotas=[], checks=STD_CHECKS):
        self.form = form
        self.all_quotas = {}
        self._do_add(quotas)
        self.checks = checks
        self.requested = requested

    def add_quotas(self, formset):
        self._do_add(self._cleaned_quotas(formset))

    def _do_add(self, quotas):
        for q in quotas:
            self.all_quotas[q['quota']] = q

    def _cleaned_quotas(self, formset):
        quotas = []
        for d in formset.cleaned_data:
            if d['id']:
                value = d['requested_quota'] \
                        if self.requested else d['quota']
                name = "%s.%s" % (
                    d['id'].resource.service_type.catalog_name,
                    d['id'].resource.quota_name)
                quotas.append({'quota': d['id'],
                               'value': value,
                               'name': name,
                               'zone': d['id'].group.zone.name})
        return quotas

    def do_checks(self):
        res = []
        for check in self.checks:
            info = check(self)
            if info:
                res.append(info)
        return res

    def get(self, quota_name, zone='nectar'):
        quotas = filter(lambda q: q['name'] == quota_name and
                        q['zone'] == zone, self.all_quotas.values())
        if len(quotas) >= 1:
            return quotas[0]['value']
        else:
            return 0

    def get_all(self, quota_name):
        return filter(lambda q: q['name'] == quota_name and
                      q['value'] > 0, self.all_quotas.values())
