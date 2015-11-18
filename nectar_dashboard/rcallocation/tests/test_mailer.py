from django.core import mail
from django.test import TestCase
import pytest

from . import factories


class EmailTest(TestCase):
    @pytest.fixture(autouse=True)
    def _template_dir(self, tmpdir, settings):
        tmpdir.chdir()
        self.template_dir = tmpdir
        settings.TEMPLATE_DIRS = [tmpdir]

    @pytest.fixture(autouse=True)
    def allocation_request(self):
        self.ar = factories.AllocationFactory()

    def _write_template(self, filename, content):
        self.template_dir.join(filename).write(content)

    def test_email_send(self):
        sender = 'no-reply@test.com'
        recipients = ['test1@test.com', 'test2@test.com', 'kispear@gmail.com']
        cc_list = ['test3@test.com']
        reply_to = 'replyt0@test.com'

        template = 'template.txt'
        self._write_template(template, 'subjectbody')

        self.ar.notify_via_e_mail(
            sender,
            recipients,
            template=template,
            cc_list=cc_list,
            reply_to=reply_to
        )
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertEqual('subject', email.subject)
        self.assertEqual('body', email.body)
        self.assertEqual(reply_to, email.headers['Reply-To'])

        for addr in recipients:
            self.assertIn(addr, email.to)

        for addr in cc_list:
            self.assertIn(addr, email.cc)
