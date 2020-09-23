from unittest import mock

from django.contrib.auth import models

from openstack_dashboard.test import helpers

from nectar_dashboard.rcallocation import quota_sanity
from nectar_dashboard.rcallocation.tests import common


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


def build_context(quotas, form=DUMMY_FORM, approver=None):
    if approver is None:
        return quota_sanity.QuotaSanityContext(quotas=quotas, form=form)
    else:
        user = models.User(username=approver)
        return quota_sanity.QuotaSanityContext(quotas=quotas, form=form,
                                               user=user, approving=True)


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
        self.assertIsNone(quota_sanity.no_vcpu_check(context))
        self.assertIsNone(quota_sanity.no_instance_check(context))
        self.assertEqual(quota_sanity.INSTANCE_VCPU,
                         quota_sanity.instance_vcpu_check(context)[0])

    def test_ram_checks(self):
        quotas = [build_quota('compute', 'cores', 1),
                  build_quota('compute', 'ram', 0)]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.nondefault_ram_check(context))

        quotas = [build_quota('compute', 'cores', 1),

                  build_quota('compute', 'ram', 4)]
        context = quota_sanity.QuotaSanityContext(quotas=quotas)
        self.assertIsNone(quota_sanity.nondefault_ram_check(context))

        quotas = [build_quota('compute', 'cores', 2),
                  build_quota('compute', 'ram', 7)]
        context = quota_sanity.QuotaSanityContext(quotas=quotas)

        self.assertEqual(quota_sanity.SMALL_MEM,
                         quota_sanity.nondefault_ram_check(context)[0])

        quotas = [build_quota('compute', 'cores', 2),
                  build_quota('compute', 'ram', 8)]
        context = quota_sanity.QuotaSanityContext(quotas=quotas)
        self.assertIsNone(quota_sanity.nondefault_ram_check(context))

        quotas = [build_quota('compute', 'cores', 2),
                  build_quota('compute', 'ram', 9)]
        context = quota_sanity.QuotaSanityContext(quotas=quotas)
        self.assertEqual(quota_sanity.LARGE_MEM,
                         quota_sanity.nondefault_ram_check(context)[0])

    def test_cinder_checks(self):
        common.sites_setup()
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 0, 'QRIScloud')]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.cinder_instance_check(context))

        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.CINDER_WITHOUT_INSTANCES,
                         quota_sanity.cinder_instance_check(context)[0])

        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.cinder_local_check(context))

        form = FakeForm({'associated_site': None})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        context = build_context(quotas, form=form)
        self.assertIsNone(quota_sanity.cinder_local_check(context))

        form = FakeForm({'associated_site': common.get_site('qcif')})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        context = build_context(quotas, form=form)
        self.assertIsNone(quota_sanity.cinder_local_check(context))

        form = FakeForm({'associated_site': common.get_site('monash')})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        context = build_context(quotas, form=form)
        self.assertEqual(quota_sanity.CINDER_NOT_LOCAL,
                         quota_sanity.cinder_local_check(context)[0])

        form = FakeForm({'associated_site': common.get_site('monash')})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'monash-03')]
        context = build_context(quotas, form=form)
        self.assertIsNone(quota_sanity.cinder_local_check(context))

    def test_trove_checks(self):
        quotas = [build_quota('database', 'instances', 0),
                  build_quota('database', 'volumes', 0)]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.trove_server_check(context))

        quotas = [build_quota('database', 'instances', 0),
                  build_quota('database', 'volumes', 1)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.TROVE_WITHOUT_SERVERS,
                         quota_sanity.trove_server_check(context)[0])

        quotas = [build_quota('database', 'instances', 0),
                  build_quota('database', 'volumes', 0)]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.trove_storage_check(context))

        quotas = [build_quota('database', 'instances', 1),
                  build_quota('database', 'volumes', 0)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.TROVE_WITHOUT_STORAGE,
                         quota_sanity.trove_storage_check(context)[0])

        quotas = [build_quota('database', 'instances', 0),
                  build_quota('database', 'volumes', 0),
                  build_quota('object', 'object', 0)]
        context = build_context(quotas)

        self.assertIsNone(quota_sanity.trove_backup_check(context))
        quotas = [build_quota('database', 'instances', 1),
                  build_quota('database', 'volumes', 1),
                  build_quota('object', 'object', 1)]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.trove_backup_check(context))
        quotas = [build_quota('database', 'instances', 0),
                  build_quota('database', 'volumes', 1),
                  build_quota('object', 'object', 1)]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.trove_backup_check(context))
        quotas = [build_quota('database', 'instances', 1),
                  build_quota('database', 'volumes', 0),
                  build_quota('object', 'object', 1)]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.trove_backup_check(context))

        quotas = [build_quota('database', 'instances', 1),
                  build_quota('database', 'volumes', 1),
                  build_quota('object', 'object', 0)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.TROVE_WITHOUT_SWIFT,
                         quota_sanity.trove_backup_check(context)[0])
        quotas = [build_quota('database', 'instances', 0),
                  build_quota('database', 'volumes', 1),
                  build_quota('object', 'object', 0)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.TROVE_WITHOUT_SWIFT,
                         quota_sanity.trove_backup_check(context)[0])
        quotas = [build_quota('database', 'instances', 1),
                  build_quota('database', 'volumes', 0),
                  build_quota('object', 'object', 0)]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.TROVE_WITHOUT_SWIFT,
                         quota_sanity.trove_backup_check(context)[0])

    def test_manila_checks(self):
        common.sites_setup()
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud-GPFS')]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.manila_local_check(context))

        form = FakeForm({'associated_site': None})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('share', 'shares', 10, 'QRIScloud-GPFS')]
        context = build_context(quotas, form=form)
        self.assertIsNone(quota_sanity.manila_local_check(context))

        form = FakeForm({'associated_site': common.get_site('uom')})
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
        self.assertIsNone(quota_sanity.neutron_checks(context))

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
        self.assertIsNone(quota_sanity.neutron_checks(context))

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

    def test_magnum_instance_check(self):
        quotas = [build_quota('container', 'clusters', 0),
                  build_quota('compute', 'instances', 0)]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.magnum_instance_check(context))

        quotas = [build_quota('container', 'clusters', 1),
                  build_quota('compute', 'instances', 2)]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.magnum_instance_check(context))

        quotas = [build_quota('container', 'clusters', 1),
                  build_quota('compute', 'instances', 0),  # no instances
        ]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.CLUSTER_WITHOUT_INSTANCES,
                         quota_sanity.magnum_instance_check(context)[0])

        quotas = [build_quota('container', 'clusters', 1),
                  build_quota('compute', 'instances', 1),  # not enough
        ]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.CLUSTER_WITHOUT_INSTANCES,
                         quota_sanity.magnum_instance_check(context)[0])

    def test_magnum_neutron_checks(self):
        quotas = [build_quota('container', 'clusters', 0)]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.magnum_neutron_checks(context))

        quotas = [build_quota('container', 'clusters', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'loadbalancer', 3),
                  build_quota('network', 'router', 1),
                  build_quota('network', 'floatingip', 2),
        ]
        context = build_context(quotas)
        self.assertIsNone(quota_sanity.magnum_neutron_checks(context))

        quotas = [build_quota('container', 'clusters', 1),
                  build_quota('network', 'network', 0),  # no network
                  build_quota('network', 'loadbalancer', 3),
                  build_quota('network', 'router', 1),
                  build_quota('network', 'floatingip', 2),
        ]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.CLUSTER_WITHOUT_NETWORK,
                         quota_sanity.magnum_neutron_checks(context)[0])

        quotas = [build_quota('container', 'clusters', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'loadbalancer', 2),  # not enough
                  build_quota('network', 'router', 1),
                  build_quota('network', 'floatingip', 2),
        ]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.CLUSTER_WITHOUT_LBS,
                         quota_sanity.magnum_neutron_checks(context)[0])

        quotas = [build_quota('container', 'clusters', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'loadbalancer', 3),
                  build_quota('network', 'router', 0),  # no router
                  build_quota('network', 'floatingip', 2),
        ]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.CLUSTER_WITHOUT_ROUTER,
                         quota_sanity.magnum_neutron_checks(context)[0])

        quotas = [build_quota('container', 'clusters', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'loadbalancer', 3),
                  build_quota('network', 'router', 1),
                  build_quota('network', 'floatingip', 1),  # not enough
        ]
        context = build_context(quotas)
        self.assertEqual(quota_sanity.CLUSTER_WITHOUT_FIPS,
                         quota_sanity.magnum_neutron_checks(context)[0])


QS_LOG = 'nectar_dashboard.rcallocation.quota_sanity.LOG'


class QuotaSanityApproverChecksTest(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.sites_setup()
        common.approvers_setup()

    def test_approver_authority_checks(self):
        quotas = [build_quota('volume', 'gigabytes', 1, 'QRIScloud')]
        context = build_context(quotas, approver="test_user")
        self.assertEqual([], quota_sanity.approver_checks(context))

    def test_not_approver(self):
        quotas = [build_quota('volume', 'gigabytes', 1, 'QRIScloud')]
        context = build_context(quotas, approver="not_a_user")
        with mock.patch(QS_LOG) as mock_log:
            self.assertEqual(quota_sanity.APPROVER_PROBLEM,
                             quota_sanity.approver_checks(context)[0])
            mock_log.warning.assert_called_once()

    def test_no_approver_sites(self):
        quotas = [build_quota('volume', 'gigabytes', 1, 'QRIScloud')]
        context = build_context(quotas, approver="test_user3")
        with mock.patch(QS_LOG) as mock_log:
            self.assertEqual(quota_sanity.APPROVER_PROBLEM,
                             quota_sanity.approver_checks(context)[0])
            mock_log.warning.assert_called_once()

    def test_approver_not_authorized(self):
        quotas = [build_quota('volume', 'gigabytes', 1, 'QRIScloud')]
        context = build_context(quotas, approver="test_user2")
        self.assertEqual(quota_sanity.APPROVER_NOT_AUTHORIZED,
                         quota_sanity.approver_checks(context)[0][0])
