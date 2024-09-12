import os

from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories
from nectar_dashboard.rcallocation import utils


class UtilsTest(base.BaseTestCase):

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
        a1 = factories.AllocationFactory.create(project_name='Fake_project')

        self.assertFalse(utils.is_project_name_available('fake-project'))
        self.assertTrue(utils.is_project_name_available('fake-project', a1))
        self.assertFalse(utils.is_project_name_available('faKe-proJect'))

        factories.AllocationFactory.create(project_name='fake-PROject1')

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

    def test_open_config_file(self):
        file_name = f"testing-{os.getpid()}.txt"
        try:
            with self.assertRaises(FileNotFoundError):
                utils.open_config_file(file_name)

            with open(f"/tmp/{file_name}", mode="w") as o:
                print("Jello world", file=o)

            i = utils.open_config_file(f"/tmp/{file_name}")
            self.assertIsNotNone(i)
            i.close()

            i = utils.open_config_file(f"file:///tmp/{file_name}")
            self.assertIsNotNone(i)
            i.close()

            i = utils.open_config_file(file_name)
            self.assertIsNotNone(i)
            i.close()
        finally:
            try:
                os.remove(f"/tmp/{file_name}")
            except FileNotFoundError:
                pass
            try:
                os.remove(file_name)
            except FileNotFoundError:
                pass
