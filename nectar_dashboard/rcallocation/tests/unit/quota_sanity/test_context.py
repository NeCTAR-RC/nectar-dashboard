from openstack_dashboard.test import helpers

from nectar_dashboard.rcallocation import quota_sanity


def build_quota(service, resource, value, zone='nectar'):
    # In a real quota row, the 'quota' will be a real `Quota` object.
    # However, all we need is something that works as a unique hash key.
    # A string does the job.
    return {
        'key': "%s.%s.%s" % (service, resource, zone),
        'name': "%s.%s" % (service, resource),
        'value': value,
        'zone': zone}


class FakeForm(object):

    def __init__(self, values):
        self.cleaned_data = values


DUMMY_FORM = FakeForm({})


def build_context(quotas, form=DUMMY_FORM):
    return quota_sanity.QuotaSanityContext(quotas=quotas, form=form)


class QuotaSanityContextTest(helpers.TestCase):
    def test_empty_context(self):
        context = quota_sanity.QuotaSanityContext()
        self.assertEqual(0, len(context.all_quotas))
        self.assertTrue(context.requested)
        self.assertIsNone(context.form)

    def test_nonempty_context(self):
        quotas = [build_quota('compute', 'instances', 1),
                  build_quota('compute', 'cores', 1)]
        context = build_context(quotas)
        self.assertEqual(0, context.get('compute.jellybeans'))
        self.assertEqual(0, context.get('compute.jellybeans'))
        self.assertEqual(1, context.get('compute.instances'))
        self.assertEqual(1, context.get('compute.instances', zone='nectar'))
        self.assertEqual(0, context.get('compute.instances', zone='venezuala'))
        self.assertEqual(1, len(context.get_all('compute.instances')))
        self.assertEqual(0, len(context.get_all('compute.jellybeans')))
        self.assertEqual(DUMMY_FORM, context.form)

    # Testing the 'add_quotas' method would entail constructing
    # a quota formset populated with semi-sensible quotas.  Hard.

    def test_do_checks(self):
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('compute', 'cores', 0)]
        context = build_context(quotas)
        res = context.do_checks()
        self.assertEqual(2, len(res))
        self.assertEqual(quota_sanity.NO_VCPU, res[0][0])
        self.assertEqual(quota_sanity.NO_INSTANCE, res[1][0])


class QuotaSanityChecksTest(helpers.TestCase):
    def test_compute_checks(self):
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('compute', 'cores', 0)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.NO_VCPU,
                         quota_sanity.no_vcpu_check(context)[0])
        self.assertEqual(quota_sanity.NO_INSTANCE,
                         quota_sanity.no_instance_check(context)[0])

    def test_compute_checks2(self):
        quotas = [build_quota('compute', 'instances', 4),
                  build_quota('compute', 'cores', 3)]
        context = quota_sanity.QuotaSanityContext(quotas=quotas)
        self.assertEqual(None, quota_sanity.no_vcpu_check(context))
        self.assertEqual(None, quota_sanity.no_instance_check(context))
        self.assertEqual(quota_sanity.INSTANCE_VCPU,
                         quota_sanity.instance_vcpu_check(context)[0])

    def test_ram_checks(self):
        quotas = [build_quota('compute', 'cores', 1),
                  build_quota('compute', 'ram', 0)]
        context = build_context(quotas)
        self.assertEqual(None, quota_sanity.nondefault_ram_check(context))

        quotas = [build_quota('compute', 'cores', 1),
                  build_quota('compute', 'ram', 4096)]
        context = build_context(quotas)
        self.assertEqual(None, quota_sanity.nondefault_ram_check(context))

        quotas = [build_quota('compute', 'cores', 2),
                  build_quota('compute', 'ram', 8191)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.SMALL_MEM,
                         quota_sanity.nondefault_ram_check(context)[0])

        quotas = [build_quota('compute', 'cores', 2),
                  build_quota('compute', 'ram', 8193)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.LARGE_MEM,
                         quota_sanity.nondefault_ram_check(context)[0])

    def test_cinder_checks(self):
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 0, 'QRIScloud')]
        context = build_context(quotas)
        self.assertEqual(None,
                         quota_sanity.cinder_instance_check(context))

        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.CINDER_WITHOUT_INSTANCES,
                         quota_sanity.cinder_instance_check(context)[0])

        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        context = build_context(quotas)
        self.assertEqual(None,
                         quota_sanity.cinder_local_check(context))

        form = FakeForm({'allocation_home': 'national'})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        context = build_context(quotas, form=form)
        self.assertEqual(None,
                         quota_sanity.cinder_local_check(context))

        form = FakeForm({'allocation_home': 'qcif'})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        context = build_context(quotas, form=form)
        self.assertEqual(None,
                         quota_sanity.cinder_local_check(context))

        form = FakeForm({'allocation_home': 'monash'})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        context = build_context(quotas, form=form)
        self.assertEqual(quota_sanity.CINDER_NOT_LOCAL,
                         quota_sanity.cinder_local_check(context)[0])

        form = FakeForm({'allocation_home': 'monash'})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'monash-03')]
        context = build_context(quotas, form=form)
        self.assertEqual(None,
                         quota_sanity.cinder_local_check(context))

    def test_manila_checks(self):
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud-GPFS')]
        context = build_context(quotas)
        self.assertEqual(None,
                         quota_sanity.manila_local_check(context))

        form = FakeForm({'allocation_home': 'national'})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('share', 'shares', 10, 'QRIScloud-GPFS')]
        context = build_context(quotas, form=form)
        self.assertEqual(None,
                         quota_sanity.manila_local_check(context))

        form = FakeForm({'allocation_home': 'monash'})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('share', 'shares', 10, 'QRIScloud-GPFS')]
        context = build_context(quotas, form=form)
        self.assertEqual(quota_sanity.MANILA_NOT_LOCAL,
                         quota_sanity.manila_local_check(context)[0])

    def test_neutron_checks(self):
        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 0),
                  build_quota('network', 'router', 0),
                  build_quota('network', 'loadbalancer', 0)]
        context = build_context(quotas)
        self.assertEqual(None, quota_sanity.neutron_checks(context))

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 0),  # missing router
                  build_quota('network', 'loadbalancer', 0)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.NO_ROUTER,
                         quota_sanity.neutron_checks(context)[0])

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 0),  # missing net
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 0)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.NO_NETWORK,
                         quota_sanity.neutron_checks(context)[0])

        quotas = [build_quota('network', 'floatingip', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 1)]
        context = build_context(quotas)
        self.assertEqual(None, quota_sanity.neutron_checks(context))

        quotas = [build_quota('network', 'floatingip', 1),
                  build_quota('network', 'network', 0),  # missing net
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 0)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.FLOATING_IP_DEP,
                         quota_sanity.neutron_checks(context)[0])

        quotas = [build_quota('network', 'floatingip', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 0),  # missing router
                  build_quota('network', 'loadbalancer', 1)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.FLOATING_IP_DEP,
                         quota_sanity.neutron_checks(context)[0])

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 0),  # missing net
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 1)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.LOAD_BALANCER_DEP,
                         quota_sanity.neutron_checks(context)[0])

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 0),  # missing router
                  build_quota('network', 'loadbalancer', 1)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.LOAD_BALANCER_DEP,
                         quota_sanity.neutron_checks(context)[0])
