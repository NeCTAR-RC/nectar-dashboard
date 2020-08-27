from openstack_dashboard.test import helpers

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories
from nectar_dashboard.rcallocation import utils


class CopyAllocationTest(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.factory_setup()

    def test_build_test_allocation(self):
        allocation = factories.AllocationFactory.create(
            contact_email='other@example.com')
        self.assertIsNone(allocation.parent_request)
        original_dict = common.allocation_to_dict(allocation)
        original_mod = allocation.modified_time

        copy_id = utils.copy_allocation(allocation).id

        # Refetch the copy from the database
        copy = models.AllocationRequest.objects.get(id=copy_id)

        # The copy's parent should refer to the allocation
        self.assertIsNone(allocation.parent_request)
        self.assertEqual(allocation.id, copy.parent_request.id)

        copy_mod = copy.modified_time
        current_mod = allocation.modified_time

        # The copy should have the same mod date as the original
        # allocation
        self.assertEqual(original_mod, copy_mod)
        self.assertEqual(original_mod, current_mod)

        # Check for any other differences after removing dict entries
        # that we've already dealt with or that we expect to be different.
        current_dict = common.allocation_to_dict(allocation)
        copy_dict = common.allocation_to_dict(copy)
        for d in [original_dict, current_dict, copy_dict]:
            d.pop('id', None)
            d.pop('parent_request', None)
            # ignore the quota tree for now
            d.pop('quota', None)
        self.maxDiff = None
        self.assertDictEqual(copy_dict, current_dict)
        self.assertDictEqual(copy_dict, original_dict)
