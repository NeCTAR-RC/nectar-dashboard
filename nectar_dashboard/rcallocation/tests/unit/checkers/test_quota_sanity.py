from unittest import mock

from django.contrib.auth import models

from openstack_dashboard.test import helpers

from nectar_dashboard.rcallocation import checkers
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


def build_checker(quotas, form=DUMMY_FORM, approver=None):
    if approver is None:
        return checkers.QuotaSanityChecker(quotas=quotas, form=form)
    else:
        user = models.User(username=approver)
        return checkers.QuotaSanityChecker(quotas=quotas, form=form,
                                               user=user, approving=True)


class QuotaSanityCheckerTest(helpers.TestCase):

    def test_empty_checker(self):
        checker = checkers.QuotaSanityChecker()
        self.assertEqual(0, len(checker.all_quotas))
        self.assertTrue(checker.requested)
        self.assertIsNone(checker.form)

    def test_nonempty_checker(self):
        quotas = [build_quota('compute', 'instances', 1),
                  build_quota('compute', 'cores', 1)]
        checker = build_checker(quotas)
        self.assertEqual(0, checker.get_quota('compute.jellybeans'))
        self.assertEqual(0, checker.get_quota('compute.jellybeans'))
        self.assertEqual(1, checker.get_quota('compute.instances'))
        self.assertEqual(1, checker.get_quota('compute.instances',
                                              zone='nectar'))
        self.assertEqual(0, checker.get_quota('compute.instances',
                                              zone='venezuala'))
        self.assertEqual(1, len(checker.get_all_quotas('compute.instances')))
        self.assertEqual(0, len(checker.get_all_quotas('compute.jellybeans')))
        self.assertEqual(DUMMY_FORM, checker.form)

    # Testing the 'add_quotas' method would entail constructing
    # a quota formset populated with semi-sensible quotas.  Hard.

    def test_do_checks(self):
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('compute', 'cores', 0)]
        checker = build_checker(quotas)
        res = checker.do_checks()
        self.assertEqual(2, len(res))
        self.assertEqual(checkers.NO_VCPU, res[0][0])
        self.assertEqual(checkers.NO_INSTANCE, res[1][0])


class QuotaSanityChecksTest(helpers.TestCase):
    def test_compute_checks(self):
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('compute', 'cores', 0)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.NO_VCPU,
                         checkers.no_vcpu_check(checker)[0])
        self.assertEqual(checkers.NO_INSTANCE,
                         checkers.no_instance_check(checker)[0])

    def test_compute_checks2(self):
        quotas = [build_quota('compute', 'instances', 4),
                  build_quota('compute', 'cores', 3)]
        checker = checkers.QuotaSanityChecker(quotas=quotas)
        self.assertIsNone(checkers.no_vcpu_check(checker))
        self.assertIsNone(checkers.no_instance_check(checker))
        self.assertEqual(checkers.INSTANCE_VCPU,
                         checkers.instance_vcpu_check(checker)[0])

    def test_ram_checks(self):
        quotas = [build_quota('compute', 'cores', 1),
                  build_quota('compute', 'ram', 0)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.nondefault_ram_check(checker))

        quotas = [build_quota('compute', 'cores', 1),

                  build_quota('compute', 'ram', 4)]
        checker = checkers.QuotaSanityChecker(quotas=quotas)
        self.assertIsNone(checkers.nondefault_ram_check(checker))

        quotas = [build_quota('compute', 'cores', 2),
                  build_quota('compute', 'ram', 7)]
        checker = checkers.QuotaSanityChecker(quotas=quotas)

        self.assertEqual(checkers.SMALL_MEM,
                         checkers.nondefault_ram_check(checker)[0])

        quotas = [build_quota('compute', 'cores', 2),
                  build_quota('compute', 'ram', 8)]
        checker = checkers.QuotaSanityChecker(quotas=quotas)
        self.assertIsNone(checkers.nondefault_ram_check(checker))

        quotas = [build_quota('compute', 'cores', 2),
                  build_quota('compute', 'ram', 9)]
        checker = checkers.QuotaSanityChecker(quotas=quotas)
        self.assertEqual(checkers.LARGE_MEM,
                         checkers.nondefault_ram_check(checker)[0])

    def test_cinder_checks(self):
        common.sites_setup()
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 0, 'QRIScloud')]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.cinder_instance_check(checker))

        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        checker = build_checker(quotas)
        self.assertEqual(checkers.CINDER_WITHOUT_INSTANCES,
                         checkers.cinder_instance_check(checker)[0])

        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.cinder_local_check(checker))

        form = FakeForm({'associated_site': None})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        checker = build_checker(quotas, form=form)
        self.assertIsNone(checkers.cinder_local_check(checker))

        form = FakeForm({'associated_site': common.get_site('qcif')})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        checker = build_checker(quotas, form=form)
        self.assertIsNone(checkers.cinder_local_check(checker))

        form = FakeForm({'associated_site': common.get_site('monash')})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        checker = build_checker(quotas, form=form)
        self.assertEqual(checkers.CINDER_NOT_LOCAL,
                         checkers.cinder_local_check(checker)[0])
        self.assertEqual('monash approved local allocation requests '
                         'volume storage in QRIScloud',
                         checkers.cinder_local_check(checker)[1])

        form = FakeForm({'associated_site': common.get_site('monash'),
                         'national': True})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud')]
        checker = build_checker(quotas, form=form)
        self.assertEqual(checkers.CINDER_NOT_LOCAL,
                         checkers.cinder_local_check(checker)[0])
        self.assertEqual('monash approved national allocation requests '
                         'volume storage in QRIScloud',
                         checkers.cinder_local_check(checker)[1])

        form = FakeForm({'associated_site': common.get_site('monash')})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'monash-03')]
        checker = build_checker(quotas, form=form)
        self.assertIsNone(checkers.cinder_local_check(checker))

    def test_trove_checks(self):
        quotas = [build_quota('database', 'ram', 0),
                  build_quota('database', 'volumes', 0)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.trove_ram_check(checker))

        quotas = [build_quota('database', 'ram', 0),
                  build_quota('database', 'volumes', 1)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.TROVE_WITHOUT_RAM,
                         checkers.trove_ram_check(checker)[0])

        # Not multiple of 4
        quotas = [build_quota('database', 'ram', 6),
                  build_quota('database', 'volumes', 0)]
        checker = build_checker(quotas)
        self.assertEqual('',
                         checkers.trove_ram_check(checker)[0])
        # RAM < 3
        quotas = [build_quota('database', 'ram', 3),
                  build_quota('database', 'volumes', 0)]
        checker = build_checker(quotas)
        self.assertEqual('',
                         checkers.trove_ram_check(checker)[0])
        # RAM > 100
        quotas = [build_quota('database', 'ram', 101),
                  build_quota('database', 'volumes', 0)]
        checker = build_checker(quotas)
        self.assertEqual('',
                         checkers.trove_ram_check(checker)[0])

        quotas = [build_quota('database', 'ram', 0),
                  build_quota('database', 'volumes', 0)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.trove_storage_check(checker))

        quotas = [build_quota('database', 'ram', 4),
                  build_quota('database', 'volumes', 0)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.TROVE_WITHOUT_STORAGE,
                         checkers.trove_storage_check(checker)[0])

        quotas = [build_quota('database', 'ram', 0),
                  build_quota('database', 'volumes', 0),
                  build_quota('object', 'object', 0)]
        checker = build_checker(quotas)

        self.assertIsNone(checkers.trove_backup_check(checker))
        quotas = [build_quota('database', 'ram', 4),
                  build_quota('database', 'volumes', 1),
                  build_quota('object', 'object', 1)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.trove_backup_check(checker))
        quotas = [build_quota('database', 'ream', 0),
                  build_quota('database', 'volumes', 1),
                  build_quota('object', 'object', 1)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.trove_backup_check(checker))
        quotas = [build_quota('database', 'ram', 4),
                  build_quota('database', 'volumes', 0),
                  build_quota('object', 'object', 1)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.trove_backup_check(checker))

        quotas = [build_quota('database', 'ram', 4),
                  build_quota('database', 'volumes', 1),
                  build_quota('object', 'object', 0)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.TROVE_WITHOUT_SWIFT,
                         checkers.trove_backup_check(checker)[0])
        quotas = [build_quota('database', 'ram', 0),
                  build_quota('database', 'volumes', 1),
                  build_quota('object', 'object', 0)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.TROVE_WITHOUT_SWIFT,
                         checkers.trove_backup_check(checker)[0])
        quotas = [build_quota('database', 'ram', 4),
                  build_quota('database', 'volumes', 0),
                  build_quota('object', 'object', 0)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.TROVE_WITHOUT_SWIFT,
                         checkers.trove_backup_check(checker)[0])

    def test_manila_checks(self):
        common.sites_setup()
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('volume', 'gigabytes', 10, 'QRIScloud-GPFS')]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.manila_local_check(checker))

        form = FakeForm({'associated_site': None})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('share', 'shares', 10, 'QRIScloud-GPFS')]
        checker = build_checker(quotas, form=form)
        self.assertIsNone(checkers.manila_local_check(checker))

        form = FakeForm({'associated_site': common.get_site('uom')})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('share', 'shares', 10, 'QRIScloud-GPFS')]
        checker = build_checker(quotas, form=form)
        self.assertEqual(checkers.MANILA_NOT_LOCAL,
                         checkers.manila_local_check(checker)[0])
        self.assertEqual('uom approved local allocation requests shares '
                         'in QRIScloud-GPFS',
                         checkers.manila_local_check(checker)[1])

        form = FakeForm({'associated_site': common.get_site('uom'),
                         'national': True})
        quotas = [build_quota('compute', 'instances', 0),
                  build_quota('share', 'shares', 10, 'QRIScloud-GPFS')]
        checker = build_checker(quotas, form=form)
        self.assertEqual(checkers.MANILA_NOT_LOCAL,
                         checkers.manila_local_check(checker)[0])
        self.assertEqual('uom approved national allocation requests shares '
                         'in QRIScloud-GPFS',
                         checkers.manila_local_check(checker)[1])

    def test_neutron_checks(self):
        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 0),
                  build_quota('network', 'router', 0),
                  build_quota('network', 'loadbalancer', 0)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.neutron_checks(checker))

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 0),  # missing router
                  build_quota('network', 'loadbalancer', 0)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.NO_ROUTER,
                         checkers.neutron_checks(checker)[0])

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 0),  # missing net
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 0)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.NO_NETWORK,
                         checkers.neutron_checks(checker)[0])

        quotas = [build_quota('network', 'floatingip', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 1)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.neutron_checks(checker))

        quotas = [build_quota('network', 'floatingip', 1),
                  build_quota('network', 'network', 0),  # missing net
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 0)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.FLOATING_IP_DEP,
                         checkers.neutron_checks(checker)[0])

        quotas = [build_quota('network', 'floatingip', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 0),  # missing router
                  build_quota('network', 'loadbalancer', 1)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.FLOATING_IP_DEP,
                         checkers.neutron_checks(checker)[0])

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 0),  # missing net
                  build_quota('network', 'router', 1),
                  build_quota('network', 'loadbalancer', 1)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.LOAD_BALANCER_DEP,
                         checkers.neutron_checks(checker)[0])

        quotas = [build_quota('network', 'floatingip', 0),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'router', 0),  # missing router
                  build_quota('network', 'loadbalancer', 1)]
        checker = build_checker(quotas)
        self.assertEqual(checkers.LOAD_BALANCER_DEP,
                         checkers.neutron_checks(checker)[0])

    def test_magnum_instance_check(self):
        quotas = [build_quota('container-infra', 'cluster', 0),
                  build_quota('compute', 'instances', 0)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.magnum_instance_check(checker))

        quotas = [build_quota('container-infra', 'cluster', 1),
                  build_quota('compute', 'instances', 2)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.magnum_instance_check(checker))

        quotas = [build_quota('container-infra', 'cluster', 1),
                  build_quota('compute', 'instances', 0),  # no instances
        ]
        checker = build_checker(quotas)
        self.assertEqual(checkers.CLUSTER_WITHOUT_INSTANCES,
                         checkers.magnum_instance_check(checker)[0])

        quotas = [build_quota('container-infra', 'cluster', 1),
                  build_quota('compute', 'instances', 1),  # not enough
        ]
        checker = build_checker(quotas)
        self.assertEqual(checkers.CLUSTER_WITHOUT_INSTANCES,
                         checkers.magnum_instance_check(checker)[0])

    def test_magnum_neutron_checks(self):
        quotas = [build_quota('container-infra', 'cluster', 0)]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.magnum_neutron_checks(checker))

        quotas = [build_quota('container-infra', 'cluster', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'loadbalancer', 3),
                  build_quota('network', 'router', 1),
                  build_quota('network', 'floatingip', 2),
        ]
        checker = build_checker(quotas)
        self.assertIsNone(checkers.magnum_neutron_checks(checker))

        quotas = [build_quota('container-infra', 'cluster', 1),
                  build_quota('network', 'network', 0),  # no network
                  build_quota('network', 'loadbalancer', 3),
                  build_quota('network', 'router', 1),
                  build_quota('network', 'floatingip', 2),
        ]
        checker = build_checker(quotas)
        self.assertEqual(checkers.CLUSTER_WITHOUT_NETWORK,
                         checkers.magnum_neutron_checks(checker)[0])

        quotas = [build_quota('container-infra', 'cluster', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'loadbalancer', 2),  # not enough
                  build_quota('network', 'router', 1),
                  build_quota('network', 'floatingip', 2),
        ]
        checker = build_checker(quotas)
        self.assertEqual(checkers.CLUSTER_WITHOUT_LBS,
                         checkers.magnum_neutron_checks(checker)[0])

        quotas = [build_quota('container-infra', 'cluster', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'loadbalancer', 3),
                  build_quota('network', 'router', 0),  # no router
                  build_quota('network', 'floatingip', 2),
        ]
        checker = build_checker(quotas)
        self.assertEqual(checkers.CLUSTER_WITHOUT_ROUTER,
                         checkers.magnum_neutron_checks(checker)[0])

        quotas = [build_quota('container-infra', 'cluster', 1),
                  build_quota('network', 'network', 1),
                  build_quota('network', 'loadbalancer', 3),
                  build_quota('network', 'router', 1),
                  build_quota('network', 'floatingip', 1),  # not enough
        ]
        checker = build_checker(quotas)
        self.assertEqual(checkers.CLUSTER_WITHOUT_FIPS,
                         checkers.magnum_neutron_checks(checker)[0])


QS_LOG = 'nectar_dashboard.rcallocation.checkers.LOG'


class QuotaSanityApproverChecksTest(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.sites_setup()
        common.approvers_setup()

    def test_approver_authority_checks(self):
        quotas = [build_quota('volume', 'gigabytes', 1, 'QRIScloud')]
        checker = build_checker(quotas, approver="test_user")
        self.assertEqual([], checkers.approver_checks(checker))

    def test_not_approver(self):
        quotas = [build_quota('volume', 'gigabytes', 1, 'QRIScloud')]
        checker = build_checker(quotas, approver="not_a_user")
        with mock.patch(QS_LOG) as mock_log:
            self.assertEqual(checkers.APPROVER_PROBLEM,
                             checkers.approver_checks(checker)[0])
            mock_log.warning.assert_called_once()

    def test_no_approver_sites(self):
        quotas = [build_quota('volume', 'gigabytes', 1, 'QRIScloud')]
        checker = build_checker(quotas, approver="test_user3")
        with mock.patch(QS_LOG) as mock_log:
            self.assertEqual(checkers.APPROVER_PROBLEM,
                             checkers.approver_checks(checker)[0])
            mock_log.warning.assert_called_once()

    def test_approver_not_authorized(self):
        quotas = [build_quota('volume', 'gigabytes', 1, 'QRIScloud')]
        checker = build_checker(quotas, approver="test_user2")
        self.assertEqual(checkers.APPROVER_NOT_AUTHORIZED,
                         checkers.approver_checks(checker)[0][0])
