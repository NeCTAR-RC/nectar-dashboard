import logging


LOG = logging.getLogger('nectar_dashboard.rcallocation')


def instanceVCPUCheck(context):
    cores = context.get('compute.cores')
    instances = context.get('compute.instances')
    if cores < instances:
        return (1, "requested instances (%d) > requested VCPUs (%d)" % 
                (instances, cores))
    else:
        return None


def noVCPUCheck(context):
    if context.get('compute.cores') == 0:
        return (2, "no VCPUs requested")
    else:
        return None


def noInstanceCheck(context):
    if context.get('compute.instances') == 0:
        return (3, "no instances requested")
    else:
        return None


def nondefaultRAMCheck(context):
    vcpus = context.get('compute.cores')
    mem = context.get('compute.memory')
    if vcpus > 0 and mem > 0:
        if vcpus * 4096 > mem:
            return (4, "non-default RAM (%d MB) > 4GB ratio" % mem)
        elif vcpus * 4096 < mem:
            return (4, "non-default RAM (%d MB) < 4GB ratio" % mem)
    return None


def cinderWithoutInstanceCheck(context):
    if context.get('compute.instances') == 0:
        for zone, value in context.get_all('volume.gigabytes'):
            if value > 0:
                return (5, 'volume storage requested without any instances')
    return None


def neutronChecks(context):
    ips = context.get('network.floatingip')
    networks = context.get('network.network')
    routers = context.get('network.router')
    loadbalancers = context.get('network.loadbalancer')
    if networks > 0 and routers == 0:
        return (6, 'use of advanced networks requires at least 1 router')
    if networks == 0 and routers > 0:
        return (7, 'use of advanced networks requires at least 1 network')
    if ips > 0 and networks == 0 and routers == 0:
        return (8, 'floating ips require at least 1 network and 1 router')
    if loadbalancers > 0 and networks == 0 and routers == 0:
        return (9, 'load balancers require at least 1 network and 1 router')


STD_CHECKS = [instanceVCPUCheck,
              noVCPUCheck,
              noInstanceCheck,
              nondefaultRAMCheck,
              cinderWithoutInstanceCheck,
              neutronChecks]


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
