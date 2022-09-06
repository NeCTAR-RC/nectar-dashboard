from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone
from openstack_dashboard.test import helpers

from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories

from nectar_dashboard.rcallocation.allocation import tables


class UrgencyTests(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.factory_setup()

    def test_get_clockstop_allocation(self):
        now = datetime.now(timezone.utc)
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=now,
            contact_email='other@example.com')
        self.assertEqual('X', allocation.status)
        self.assertEqual(now, allocation.modified_time)
        _ = factories.AllocationFactory.create(
            status='A', modified_time=(now - timedelta(days=3)),
            parent_request=allocation,
            contact_email='other@example.com')
        _ = factories.AllocationFactory.create(
            status='A', modified_time=(now - timedelta(days=5)),
            parent_request=allocation,
            contact_email='other@example.com')

        res = tables.get_clockstop_amendment(allocation)
        self.assertEqual(res.id, allocation.id)

        # Now add an earlier 'X' record
        first = factories.AllocationFactory.create(
            status='X', modified_time=now - timedelta(days=1),
            parent_request=allocation,
            contact_email='other@example.com')
        res = tables.get_clockstop_amendment(allocation)
        self.assertEqual(res.id, first.id)

        # Now add an 'X' record before the last 'A' record
        _ = factories.AllocationFactory.create(
            status='X', modified_time=now - timedelta(days=4),
            parent_request=allocation,
            contact_email='other@example.com')
        res = tables.get_clockstop_amendment(allocation)
        self.assertEqual(res.id, first.id)

    @patch('nectar_dashboard.rcallocation.allocation'
           '.tables.get_clockstop_amendment')
    def test_get_urgency(self, mock_clockstop):
        now = datetime.now(timezone.utc)
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=now)
        self.assertEqual(tables.NEW, tables.get_urgency(allocation))
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=(now - timedelta(days=8)))
        self.assertEqual(tables.ATTENTION, tables.get_urgency(allocation))
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=(now - timedelta(days=15)))
        self.assertEqual(tables.WARNING, tables.get_urgency(allocation))
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=(now - timedelta(days=22)))
        self.assertEqual(tables.OVERDUE, tables.get_urgency(allocation))
        mock_clockstop.assert_not_called()

        allocation = factories.AllocationFactory.create(
            status='X', modified_time=(now - timedelta(days=22)),
            end_date=now.date())
        self.assertEqual(tables.OVERDUE, tables.get_urgency(allocation))
        mock_clockstop.assert_not_called()

        allocation = factories.AllocationFactory.create(
            status='X', modified_time=now,
            end_date=(now.date() - timedelta(days=1)))
        mock_clockstop.return_value = allocation
        self.assertEqual(tables.EXPIRED, tables.get_urgency(allocation))
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=now,
            end_date=(now.date() - timedelta(days=15)))
        mock_clockstop.return_value = allocation
        self.assertEqual(tables.STOPPED, tables.get_urgency(allocation))
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=now,
            end_date=(now.date() - timedelta(days=29)))
        mock_clockstop.return_value = allocation
        self.assertEqual(tables.ARCHIVED, tables.get_urgency(allocation))

        allocation = factories.AllocationFactory.create(
            status='X', modified_time=(now - timedelta(days=151)),
            end_date=(now.date() - timedelta(days=1)))
        mock_clockstop.return_value = allocation
        self.assertEqual(tables.DANGER, tables.get_urgency(allocation))

        allocation = factories.AllocationFactory.create(
            status='X', modified_time=(now - timedelta(days=151)),
            end_date=(now.date() - timedelta(days=1)))
        mock_clockstop.return_value = None
        self.assertEqual(tables.UNKNOWN, tables.get_urgency(allocation))
