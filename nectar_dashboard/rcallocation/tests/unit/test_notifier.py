from unittest import mock

from django.conf import settings

from nectar_dashboard.rcallocation import notifier
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories


FAKE_FD_API = mock.MagicMock()
FAKE_FD_API_CLASS = mock.MagicMock(return_value=FAKE_FD_API)
FAKE_EMAIL_MESSAGE = mock.MagicMock()
FAKE_EMAIL_MESSAGE_CLASS = mock.MagicMock(return_value=FAKE_EMAIL_MESSAGE)


class FakeTicket(object):
    def __init__(self, id):
        self.id = id


class FakeSettings(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@mock.patch('nectar_dashboard.rcallocation.notifier.API',
            new=FAKE_FD_API_CLASS)
@mock.patch('nectar_dashboard.rcallocation.notifier.EmailMessage',
            new=FAKE_EMAIL_MESSAGE_CLASS)
class NotifierTests(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.allocation = factories.AllocationFactory.create(
            contact_email='other@example.com')

    def test_create_notifier(self):
        FAKE_SETTINGS = FakeSettings(
            ALLOCATION_EMAIL_FROM="someone@somewhere",
            ALLOCATION_EMAIL_REPLY_TO=("noone@somewhere",),
            ALLOCATION_EMAIL_CC_RECIPIENTS=[],
            ALLOCATION_EMAIL_BCC_RECIPIENTS=[])
        with mock.patch('nectar_dashboard.rcallocation.notifier.settings',
                         new=FAKE_SETTINGS):
            n = notifier.create_notifier(self.allocation)
            self.assertEqual('SMTPNotifier', n.__class__.__name__)
            self.assertEqual(self.allocation, n.allocation)
        FAKE_SETTINGS = FakeSettings(
            ALLOCATION_NOTIFIER='smtp',
            ALLOCATION_EMAIL_FROM="someone@somewhere",
            ALLOCATION_EMAIL_REPLY_TO=("noone@somewhere",),
            ALLOCATION_EMAIL_CC_RECIPIENTS=[],
            ALLOCATION_EMAIL_BCC_RECIPIENTS=[])
        with mock.patch('nectar_dashboard.rcallocation.notifier.settings',
                         new=FAKE_SETTINGS):
            n = notifier.create_notifier(self.allocation)
            self.assertEqual('SMTPNotifier', n.__class__.__name__)
            self.assertEqual(self.allocation, n.allocation)
        FAKE_SETTINGS = FakeSettings(
            ALLOCATION_NOTIFIER='freshdesk',
            FRESHDESK_GROUP_ID='1',
            FRESHDESK_EMAIL_CONFIG_ID='3',
            FRESHDESK_DOMAIN='dhd@somewhere',
            FRESHDESK_KEY='secret',
            ALLOCATION_EMAIL_CC_RECIPIENTS=[],
            ALLOCATION_EMAIL_BCC_RECIPIENTS=[])
        with mock.patch('nectar_dashboard.rcallocation.notifier.settings',
                         new=FAKE_SETTINGS):
            n = notifier.create_notifier(self.allocation)
            self.assertEqual('FreshdeskNotifier', n.__class__.__name__)
            self.assertEqual(self.allocation, n.allocation)
        FAKE_SETTINGS = FakeSettings(
            ALLOCATION_NOTIFIER='fnord')
        with mock.patch('nectar_dashboard.rcallocation.notifier.settings',
                         new=FAKE_SETTINGS):
            with self.assertRaises(RuntimeError) as cm:
                n = notifier.create_notifier(self.allocation)
            self.assertEqual("Unknown notifier choice: 'fnord'",
                             str(cm.exception))

    def test_freshdesk_life_cycle(self):
        FAKE_FD_API.reset_mock()
        n = notifier.FreshdeskNotifier(self.allocation)
        self.assertEqual(FAKE_FD_API, n.api)
        self.assertEqual(self.allocation, n.allocation)
        self.assertEqual(1, n.group_id)
        self.assertEqual(settings.ALLOCATION_EMAIL_CC_RECIPIENTS, n.cc_emails)
        self.assertEqual((), n.bcc_emails)
        self.assertEqual(123, n.email_config_id)

    def test_smtp_life_cycle(self):
        FAKE_FD_API.reset_mock()
        n = notifier.SMTPNotifier(self.allocation)
        self.assertEqual(self.allocation, n.allocation)
        self.assertEqual('allocations@nectar.org.au', n.from_email)
        self.assertEqual(['noreply@nectar.org.au'], n.reply_to)
        self.assertEqual(settings.ALLOCATION_EMAIL_CC_RECIPIENTS, n.cc_emails)
        self.assertEqual((), n.bcc_emails)

    def test_send_email_freshdesk(self):
        FAKE_FD_API.tickets.create_outbound_email.return_value = \
            FakeTicket(id="12345")
        n = notifier.FreshdeskNotifier(self.allocation)
        n.send_email("someone@example.com", "testing", "123")

        FAKE_FD_API.tickets.create_outbound_email.assert_called_once_with(
            subject='testing', description='123',
            email='someone@example.com', email_config_id=123,
            group_id=1, cc_emails=settings.ALLOCATION_EMAIL_CC_RECIPIENTS,
            bcc_emails=(),
            tags=[f"allocation-{self.allocation.id}"])

    def test_send_email_smtp(self):
        n = notifier.SMTPNotifier(self.allocation)
        n.send_email("someone@example.com", "testing", "123")

        FAKE_EMAIL_MESSAGE.send.assert_called_once_with()
        FAKE_EMAIL_MESSAGE_CLASS.assert_called_once_with(
            to=('someone@example.com',),
            from_email='allocations@nectar.org.au',
            cc=settings.ALLOCATION_EMAIL_CC_RECIPIENTS, bcc=(),
            reply_to=['noreply@nectar.org.au'],
            subject='testing', body='123')
