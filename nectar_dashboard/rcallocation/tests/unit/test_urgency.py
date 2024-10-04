from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories

from nectar_dashboard.rcallocation import urgency


class UrgencyTests(base.BaseTestCase):
    def test_get_clockstop_allocation(self):
        now = datetime.now(timezone.utc)
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=now, contact_email='other@example.com'
        )
        self.assertEqual('X', allocation.status)
        self.assertEqual(now, allocation.modified_time)
        _ = factories.AllocationFactory.create(
            status='A',
            modified_time=(now - timedelta(days=3)),
            parent_request=allocation,
            contact_email='other@example.com',
        )
        _ = factories.AllocationFactory.create(
            status='A',
            modified_time=(now - timedelta(days=5)),
            parent_request=allocation,
            contact_email='other@example.com',
        )

        res = urgency.get_clockstop_amendment(allocation)
        self.assertEqual(res.id, allocation.id)

        # Now add an earlier 'X' record
        first = factories.AllocationFactory.create(
            status='X',
            modified_time=now - timedelta(days=1),
            parent_request=allocation,
            contact_email='other@example.com',
        )
        res = urgency.get_clockstop_amendment(allocation)
        self.assertEqual(res.id, first.id)

        # Now add an 'X' record before the last 'A' record
        _ = factories.AllocationFactory.create(
            status='X',
            modified_time=now - timedelta(days=4),
            parent_request=allocation,
            contact_email='other@example.com',
        )
        res = urgency.get_clockstop_amendment(allocation)
        self.assertEqual(res.id, first.id)

    @patch('nectar_dashboard.rcallocation.urgency.get_clockstop_amendment')
    def test_get_urgency(self, mock_clockstop):
        now = datetime.now(timezone.utc)
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=now
        )
        self.assertEqual(urgency.NEW, urgency.get_urgency(allocation))
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=(now - timedelta(days=8))
        )
        self.assertEqual(urgency.ATTENTION, urgency.get_urgency(allocation))
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=(now - timedelta(days=15))
        )
        self.assertEqual(urgency.WARNING, urgency.get_urgency(allocation))
        allocation = factories.AllocationFactory.create(
            status='X', modified_time=(now - timedelta(days=22))
        )
        self.assertEqual(urgency.OVERDUE, urgency.get_urgency(allocation))
        mock_clockstop.assert_not_called()

        allocation = factories.AllocationFactory.create(
            status='X',
            modified_time=(now - timedelta(days=22)),
            end_date=now.date(),
        )
        self.assertEqual(urgency.OVERDUE, urgency.get_urgency(allocation))
        mock_clockstop.assert_not_called()

        allocation = factories.AllocationFactory.create(
            status='X',
            modified_time=now,
            end_date=(now.date() - timedelta(days=1)),
        )
        mock_clockstop.return_value = allocation
        self.assertEqual(urgency.EXPIRED, urgency.get_urgency(allocation))
        allocation = factories.AllocationFactory.create(
            status='X',
            modified_time=now,
            end_date=(now.date() - timedelta(days=15)),
        )
        mock_clockstop.return_value = allocation
        self.assertEqual(urgency.STOPPED, urgency.get_urgency(allocation))
        allocation = factories.AllocationFactory.create(
            status='X',
            modified_time=now,
            end_date=(now.date() - timedelta(days=29)),
        )
        mock_clockstop.return_value = allocation
        self.assertEqual(urgency.ARCHIVED, urgency.get_urgency(allocation))

        allocation = factories.AllocationFactory.create(
            status='X',
            modified_time=(now - timedelta(days=151)),
            end_date=(now.date() - timedelta(days=1)),
        )
        mock_clockstop.return_value = allocation
        self.assertEqual(urgency.DANGER, urgency.get_urgency(allocation))

        allocation = factories.AllocationFactory.create(
            status='X',
            modified_time=(now - timedelta(days=151)),
            end_date=(now.date() - timedelta(days=1)),
        )
        mock_clockstop.return_value = None
        self.assertEqual(urgency.UNKNOWN, urgency.get_urgency(allocation))
