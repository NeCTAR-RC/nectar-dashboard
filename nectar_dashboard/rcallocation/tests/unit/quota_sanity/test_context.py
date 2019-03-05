from django.test import testcases

from nectar_dashboard.rcallocation.quota_sanity import \
    QuotaSanityContext, NO_VCPU, NO_INSTANCE, INSTANCE_VCPU, \
    SMALL_MEM, LARGE_MEM, CINDER_WITHOUT_INSTANCES, NO_NETWORK, NO_ROUTER, \
    FLOATING_IP_DEP, LOAD_BALANCER_DEP, no_vcpu_check, no_instance_check, \
    instance_vcpu_check, nondefault_ram_check, cinder_without_instance_check, \
    neutron_checks


def build_quota(service, resource, value, zone='nectar'):
    # In a real quota row, the 'quota' will be a real `Quota` object.
    # However, all we need is something that works as a unique hash key.
    # A string does the job.
    return {
        'quota': "%s.%s.%s" % (service, resource, zone),  # Fake!
        'name': "%s.%s" % (service, resource),
        'value': value,
        'zone': zone}


class QuotaSanityContextTest(testcases.TestCase):
    def test_empty_context(self):
        context = QuotaSanityContext(None)
        self.assertEqual(0, len(context.all_quotas))
        self.assertEqual(None, context.form)
        self.assertTrue(context.requested)

    def test_nonempty_context(self):
        quotas = [build_quota('compute', 'instances', 1),
                  build_quota('compute', 'cores', 1)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(0, context.get('compute.jellybeans'))
        self.assertEqual(0, context.get('compute.jellybeans'))
        self.assertEqual(1, context.get('compute.instances'))
        self.assertEqual(1, context.get('compute.instances', zone='nectar'))
        self.assertEqual(0, context.get('compute.instances', zone='venezuala'))
        self.assertEqual(1, len(context.get_all('compute.instances')))
        self.assertEqual(0, len(context.get_all('compute.jellybeans')))

    # Testing the 'add_quotas' method would entail constructing
    # a quota formset populated with semi-sensible quotas.  Hard.

    def test_do_checks(self):
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('compute', 'cores', 0)]
        context = QuotaSanityContext(None, quotas=quotas)
        res = context.do_checks()
        self.assertEqual(2, len(res))
        self.assertEqual(NO_VCPU, res[0][0])
        self.assertEqual(NO_INSTANCE, res[1][0])


class QuotaSanityChecksTest(testcases.TestCase):
    def test_compute_checks(self):
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('compute', 'cores', 0)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(NO_VCPU, no_vcpu_check(context)[0])
        self.assertEqual(NO_INSTANCE, no_instance_check(context)[0])

    def test_compute_checks2(self):
        quotas = [build_quota('compute', 'instances', 4),
                  build_quota('compute', 'cores', 3)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(None, no_vcpu_check(context))
        self.assertEqual(None, no_instance_check(context))
        self.assertEqual(INSTANCE_VCPU, instance_vcpu_check(context)[0])

    def test_ram_checks(self):
        quotas = [build_quota('compute', 'cores', 1),
                  build_quota('compute', 'memory', 0)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(None, nondefault_ram_check(context))

        quotas = [build_quota('compute', 'cores', 1),
                  build_quota('compute', 'memory', 4096)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(None, nondefault_ram_check(context))

        quotas = [build_quota('compute', 'cores', 2),
                  build_quota('compute', 'memory', 8191)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(SMALL_MEM, nondefault_ram_check(context)[0])

        quotas = [build_quota('compute', 'cores', 2),
                  build_quota('compute', 'memory', 8193)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(LARGE_MEM, nondefault_ram_check(context)[0])

    def test_cinder_checks(self):
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 0, 'qriscloud')]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(None, cinder_without_instance_check(context))

        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'qriscloud')]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(CINDER_WITHOUT_INSTANCES,
                         cinder_without_instance_check(context)[0])

    def test_neutron_checks(self):
        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 0),
                  build_quota('network', 'router', 0),
                  build_quota('network', 'loadbalancer', 0)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(None, neutron_checks(context))

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 0),  # missing router
                  build_quota('network', 'loadbalancer', 0)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(NO_ROUTER, neutron_checks(context)[0])

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 0),  # missing net
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 0)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(NO_NETWORK, neutron_checks(context)[0])

        quotas = [build_quota('network', 'floatingip', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 1)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(None, neutron_checks(context))

        quotas = [build_quota('network', 'floatingip', 1),
                  build_quota('network', 'network', 0),  # missing net
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 0)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(FLOATING_IP_DEP, neutron_checks(context)[0])

        quotas = [build_quota('network', 'floatingip', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 0),  # missing router
                  build_quota('network', 'loadbalancer', 1)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(FLOATING_IP_DEP, neutron_checks(context)[0])

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 0),  # missing net
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 1)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(LOAD_BALANCER_DEP, neutron_checks(context)[0])

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 0),  # missing router
                  build_quota('network', 'loadbalancer', 1)]
        context = QuotaSanityContext(None, quotas=quotas)
        self.assertEqual(LOAD_BALANCER_DEP, neutron_checks(context)[0])
