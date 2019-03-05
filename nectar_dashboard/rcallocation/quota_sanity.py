import logging


LOG = logging.getLogger('nectar_dashboard.rcallocation')

# The following warning code numbers will used as anchors in the
# support page that contains "more information" about the errors.
# The values should be stable and unique.
INSTANCE_VCPU_CODE = 1
NO_VCPU_CODE = 2
NO_INSTANCE_CODE = 3
LARGE_MEM_CODE = 4
SMALL_MEM_CODE = 5
CINDER_WITHOUT_INSTANCES_CODE = 6
NO_ROUTER_CODE = 7
NO_NETWORK_CODE = 8
FLOATING_IP_DEP_CODE = 9
LOAD_BALANCER_DEP_CODE = 10


def instance_vcpu_check(context):
    cores = context.get('compute.cores')
    instances = context.get('compute.instances')
    if cores < instances:
        return (INSTANCE_VCPU_CODE,
                "requested instances (%d) > requested VCPUs (%d)" %
                (instances, cores))
    else:
        return None


def no_vcpu_check(context):
    if context.get('compute.cores') == 0:
        return (NO_VCPU_CODE, "no VCPUs requested")
    else:
        return None


def no_instance_check(context):
    if context.get('compute.instances') == 0:
        return (NO_INSTANCE_CODE, "no instances requested")
    else:
        return None


def nondefault_ram_check(context):
    vcpus = context.get('compute.cores')
    mem = context.get('compute.memory')
    if vcpus > 0 and mem > 0:
        if vcpus * 4096 > mem:
            return (LARGE_MEM_CODE,
                    "non-default RAM (%d MB) > 4GB ratio" % mem)
        elif vcpus * 4096 < mem:
            return (SMALL_MEM_CODE,
                    "non-default RAM (%d MB) < 4GB ratio" % mem)
    return None


def cinder_without_instance_check(context):
    if context.get('compute.instances') == 0:
        for zone, value in context.get_all('volume.gigabytes'):
            if value > 0:
                return (CINDER_WITHOUT_INSTANCES_CODE,
                        'volume storage requested without any instances')
    return None


def neutron_checks(context):
    ips = context.get('network.floatingip')
    networks = context.get('network.network')
    routers = context.get('network.router')
    loadbalancers = context.get('network.loadbalancer')
    if networks > 0 and routers == 0:
        return (NO_ROUTER_CODE,
                'use of advanced networks requires at least 1 router')
    if networks == 0 and routers > 0:
        return (NO_NETWORK_CODE,
                'use of advanced networks requires at least 1 network')
    if ips > 0 and networks == 0 and routers == 0:
        return (FLOATING_IP_DEP_CODE,
                'floating ips require at least 1 network and 1 router')
    if loadbalancers > 0 and networks == 0 and routers == 0:
        return (LOAD_BALANCER_DEP_CODE,
                'load balancers require at least 1 network and 1 router')


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
