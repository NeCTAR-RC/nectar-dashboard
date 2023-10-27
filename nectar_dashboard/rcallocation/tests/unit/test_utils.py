from openstack_dashboard.test import helpers

from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories
from nectar_dashboard.rcallocation import utils


class UtilsTest(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.factory_setup()

    def test_copy_allocation(self):
        self.maxDiff = 20000
        allocation = factories.AllocationFactory.create(
            contact_email=self.user.name)

        old_allocation = utils.copy_allocation(allocation)

        def _discard_different_attrs(a):
            a.pop('id')
            a.pop('parent_request')
            return a

        allocation_dict = _discard_different_attrs(
            common.allocation_to_dict(allocation))
        old_allocation_dict = _discard_different_attrs(
            common.allocation_to_dict(old_allocation))

        self.assertEqual(allocation_dict, old_allocation_dict)
        self.assertEqual(allocation.id, old_allocation.parent_request_id)

    def test_is_project_name_available(self):
        factories.AllocationFactory.create(project_name='Fake_project')
        factories.AllocationFactory.create(project_name='fake-PROject1')
        self.assertFalse(utils.is_project_name_available('fake-project'))
        self.assertFalse(utils.is_project_name_available('faKe-proJect'))
        self.assertFalse(utils.is_project_name_available('Fake_project1'))
        self.assertTrue(utils.is_project_name_available('Fake_project2'))

    def test_get_member_map(self):
        member_map = utils.get_member_map()
        self.assertEqual(1, len(member_map['ardc.edu.au']))
        self.assertEqual('ardc', member_map['ardc.edu.au'][0].name)
        self.assertEqual(2, len(member_map['csiro.au']))

    def test_sites_from_email(self):
        self.assertEqual(1,
                         len(utils.sites_from_email("ab.cd@ardc.edu.au")))
        self.assertEqual('ardc',
                         utils.sites_from_email("ab.cd@ardc.edu.au")[0].name)
        self.assertEqual('uom',
                         utils.sites_from_email(
                             "ab.cd@student.unimelb.edu.au")[0].name)
        self.assertEqual('uom',
                         utils.sites_from_email(
                             "ab.cd@exchange.unimelb.edu.au")[0].name)
        self.assertEqual('qcif',
                         utils.sites_from_email(
                             "ab.cd@student.griffithuni.edu.au")[0].name)
        self.assertEqual(2,
                         len(utils.sites_from_email("ab.cd@csiro.au")))
        self.assertEqual(0,
                         len(utils.sites_from_email("ab.cd@gmail.com")))
