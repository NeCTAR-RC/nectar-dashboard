import logging

from django.conf import settings
from django.core.mail import EmailMessage

from freshdesk.v2.api import API


LOG = logging.getLogger(__name__)


def create_notifier(allocation):
    # Backward compatibility: use 'smtp' if no setting found.
    choice = getattr(settings, 'ALLOCATION_NOTIFIER', 'smtp')
    if choice == 'smtp':
        return SMTPNotifier(allocation)
    elif choice == 'freshdesk':
        return FreshdeskNotifier(allocation)
    else:
        raise RuntimeError(f"Unknown notifier choice: '{choice}'")


class NotifierBase(object):
    expects_html = False

    def __init__(self, allocation):
        self.allocation = allocation

    def send_email(self, email, subject, body) -> str:
        raise NotImplementedError('send_email')

    def create_ticket(self, email, subject, body) -> str:
        raise NotImplementedError('create_ticket')


class SMTPNotifier(NotifierBase):
    def __init__(self, allocation):
        super().__init__(allocation)
        self.cc_emails = settings.ALLOCATION_EMAIL_CC_RECIPIENTS
        self.bcc_emails = settings.ALLOCATION_EMAIL_BCC_RECIPIENTS
        self.from_email = settings.ALLOCATION_EMAIL_FROM
        self.reply_to = [settings.ALLOCATION_EMAIL_REPLY_TO]

    def send_email(self, email, subject, body):
        email = EmailMessage(to=(email,),
                             from_email=self.from_email,
                             cc=self.cc_emails,
                             bcc=self.bcc_emails,
                             reply_to=self.reply_to,
                             subject=subject,
                             body=body)
        email.send()


class FreshdeskNotifier(NotifierBase):
    expects_html = True

    def __init__(self, allocation):
        super().__init__(allocation)
        self.group_id = int(settings.FRESHDESK_GROUP_ID)
        self.email_config_id = int(settings.FRESHDESK_EMAIL_CONFIG_ID)
        self.allocation = allocation
        self.api = API(settings.FRESHDESK_DOMAIN, settings.FRESHDESK_KEY)
        self.cc_emails = settings.ALLOCATION_EMAIL_CC_RECIPIENTS
        self.bcc_emails = settings.ALLOCATION_EMAIL_BCC_RECIPIENTS

    def send_email(self, email, subject, body) -> str:
        ticket = self.api.tickets.create_outbound_email(
            subject=subject,
            description=body,
            email=email,
            cc_emails=self.cc_emails,
            bcc_emails=self.bcc_emails,
            email_config_id=self.email_config_id,
            group_id=self.group_id,
            tags=[f"allocation-{self.allocation.id}"])
        ticket_id = ticket.id
        LOG.info(f"Allocation {self.allocation.id}: Created outbound email "
                 f"ticket {ticket_id} with requester={email}, "
                 f"cc={self.cc_emails}, bcc={self.bcc_emails}")
        return ticket_id

    def create_ticket(self, user, approver, subject, body, note):
        ticket = self.api.tickets.create(
            subject=subject,
            description=body,
            requester=user,
            assigned_agent=approver,
            email_config_id=self.email_config_id,
            group_id=self.group_id,
            tags=[f"allocation-{self.allocation.id}"])
        ticket_id = ticket.id
        LOG.info(f"Allocation {self.allocation.id}: Created ticket "
                 f"ticket {ticket_id} with requester={user}, "
                 f"agent={approver}")
        return ticket_id

    def update_ticket(self, ticket_id, text, cc_emails=[]):
        self.api.comments.create_reply(ticket_id, body=text,
                                       cc_emails=cc_emails)
        LOG.info(f"Allocation {self.allocation.id}: Sent reply to "
                 f"ticket {ticket_id}")

    def update_ticket_requester(self, ticket_id, owner):
        self.api.tickets.update_ticket(ticket_id, email=owner)
        LOG.debug(f"Allocation {self.allocation.id}: Set ticket requester "
                  f"for ticket {ticket_id} to {owner}")

    def add_note_to_ticket(self, ticket_id, text):
        self.api.comments.create_note(ticket_id, text)
        LOG.info(f"Allocation {self.allocation.id}: Added private note "
                 f"to ticket {ticket_id}")
