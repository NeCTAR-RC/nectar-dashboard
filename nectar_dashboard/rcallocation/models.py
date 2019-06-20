# Models for the ResearchCloud Allocations portal
# Original: Tom Fifield <fifieldt@unimelb.edu.au> - 2011-10
# Modified by Martin Paulo
import datetime
import logging

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.template.loader import get_template
from django.utils import timezone

from nectar_dashboard.rcallocation import allocation_home_choices
from nectar_dashboard.rcallocation import for_choices
from nectar_dashboard.rcallocation import grant_type
from nectar_dashboard.rcallocation import project_duration_choices


LOG = logging.getLogger(__name__)


#############################################################################
#
# Requests are created by Users who wish to receive Allocations
#
#############################################################################


def _six_months_from_now():
    return datetime.date.today() + datetime.timedelta(
        days=30 * 6)


class AllocationRequest(models.Model):
    NEW = 'N'
    SUBMITTED = 'E'
    APPROVED = 'A'
    DECLINED = 'R'
    UPDATE_PENDING = 'X'
    UPDATE_DECLINED = 'J'
    DELETED = 'D'

    REQUEST_STATUS_CHOICES = (
        # Request created but nothing else
        # User can: Submit
        (NEW, 'New'),

        # Request has been emailed
        # Admin can: Approve, Reject, Edit
        # User can: Edit
        (SUBMITTED, 'Submitted'),

        # Admin has approved the request
        # Admin can: Provision, Edit
        # User can: Amend, Extend
        (APPROVED, 'Approved'),

        # Admin has rejected the request
        # User can: Edit, Submit
        (DECLINED, 'Declined'),

        # User has requested an extension
        # Admin can: Approve, Reject, Edit
        # User can: Edit
        (UPDATE_PENDING, 'Update requested'),

        # Admin has rejected an extension
        # User can: Edit, Extend
        (UPDATE_DECLINED, 'Update declined'),

        # Requests in above status can be viewed by both user
        # and admin at all times.

        # Allocation has been deleted
        (DELETED, 'Deleted'),
    )
    parent_request = models.ForeignKey('AllocationRequest', null=True,
                                       blank=True)

    status = models.CharField(max_length=1, blank=False,
                              choices=REQUEST_STATUS_CHOICES,
                              default=SUBMITTED)

    status_explanation = models.TextField(
        null=True, blank=True,
        verbose_name="Reason",
        help_text="A brief explanation of the reason the request has been "
                  "sent back to the user for changes")

    created_by = models.CharField(null=False, blank=False, max_length=100)

    submit_date = models.DateField('Submission Date',
                                   default=datetime.date.today)
    modified_time = models.DateTimeField('Modified Date',
                                         default=timezone.now)

    # The ordering of the following fields are important, as it
    # governs the order they appear on the forms
    project_name = models.CharField(
        'Project identifier',
        max_length=64,
        blank=True,
        null=True,
        help_text='A short name used to identify your project.<br>'
                  'Must contain only letters and numbers.<br>'
                  '16 characters max.')

    project_description = models.CharField(
        'Project allocation title',
        max_length=200,
        help_text='A human-friendly descriptive name for your research '
                  'project.')

    contact_email = models.EmailField(
        'Contact e-mail', blank=True,
        help_text="""The e-mail address provided by your IdP which
                     will be used to communicate with you about this
                     allocation request.  <strong>Note:</strong> <i>if
                     this is not a valid e-mail address you will not
                     receive communications on any allocation request
                     you make</i>. If invalid please contact your IdP
                     and ask them to correct your e-mail address!"""
    )

    start_date = models.DateField(
        'Start date',
        default=datetime.date.today,
        help_text="""The day on which you want your Project Allocation to
                     go live. Format: yyyy-mm-dd""")

    end_date = models.DateField(
        'Estimated end date',
        editable=False,
        default=_six_months_from_now,
        help_text='The day on which your project will end.')

    estimated_project_duration = models.IntegerField(
        'Estimated project duration',
        choices=project_duration_choices.DURATION_CHOICE,
        blank=False,
        null=False,
        default=1,
        help_text="""Resources are approved for at most 12-months,
                    but projects can extend a request for resources
                    once it has been approved.""")

    convert_trial_project = models.BooleanField(
        'Convert trial project?',
        default=False,
        help_text='If selected, your existing trial project pt- will be '
                  'renamed so any resources inside it will become part of '
                  'this new allocation. A new trial project will be created '
                  'in its place.')

    approver_email = models.EmailField('Approver email', blank=True)

    use_case = models.TextField(
        "Research use case and justification",
        max_length=4096,
        help_text="""Provide a very brief overview of your research project,
        and how you will use the cloud to support your project.""")

    usage_patterns = models.TextField(
        "Instance, Object Storage and Volumes Storage Usage Patterns",
        max_length=1024, blank=True,
        help_text="""Will your project have many users and small data
        sets? Or will it have large data sets with a small number of users?
        Will your instances be long running or created and deleted as needed
        Your answers here will help us.""")

    requested_allocation_home = models.CharField(
        "Allocation home location",
        choices=allocation_home_choices.ALLOC_HOME_CHOICE[:-1],
        blank=False,
        null=False,
        default='national',
        max_length=128,
        help_text="""You can provide a primary location where you expect to
                use most resources, effectively the main Nectar site for your
                allocation. Use of other locations is still possible.
                This can also indicate a specific arrangement with a
                Nectar site, for example where you obtain support, or if
                your institution is a supporting member of that site.
                Select unassigned if you have no preference.
                """
    )

    geographic_requirements = models.TextField(
        max_length=1024,
        blank=True,
        verbose_name="Additional location requirements",
        help_text="""Indicate to the allocations committee any special
                geographic requirements that you may need, e.g. to run
                at more than one node.""")

    project_id = models.CharField(max_length=36, blank=True, null=True)

    estimated_number_users = models.IntegerField(
        'Estimated number of users',
        default='1',
        validators=[MinValueValidator(1), ],
        error_messages={
            'min_value': 'The estimated number of users must be great than 0'},
        help_text="""Estimated number of users, researchers and collaborators
        to be supported by the allocation.""")

    FOR_CHOICES = for_choices.FOR_CHOICES
    PERCENTAGE_CHOICES = (
        (0, '0%'),
        (10, '10%'),
        (20, '20%'),
        (30, '30%'),
        (40, '40%'),
        (50, '50%'),
        (60, '60%'),
        (70, '70%'),
        (80, '80%'),
        (90, '90%'),
        (100, '100%'),
    )

    field_of_research_1 = models.CharField(
        "First Field Of Research",
        choices=FOR_CHOICES,
        blank=True,
        null=True,
        max_length=6
    )

    for_percentage_1 = models.IntegerField(
        choices=PERCENTAGE_CHOICES, default=100,
        help_text="""The percentage""")

    field_of_research_2 = models.CharField(
        "Second Field Of Research",
        choices=FOR_CHOICES,
        blank=True,
        null=True,
        max_length=6
    )

    for_percentage_2 = models.IntegerField(
        choices=PERCENTAGE_CHOICES, default=0,
        help_text="""The percentage""")

    field_of_research_3 = models.CharField(
        "Third Field Of Research",
        choices=FOR_CHOICES,
        blank=True,
        null=True,
        max_length=6
    )

    for_percentage_3 = models.IntegerField(
        choices=PERCENTAGE_CHOICES, default=0)

    nectar_support = models.CharField(
        """List any ANDS, Nectar, or RDS funded projects supporting this
        request.""",
        blank=True,
        max_length=255,
        help_text="""Specify any ANDS, Nectar, RDS or ARDC capabilities
                    supporting this request.""")

    ncris_support = models.CharField(
        'List NCRIS capabilities supporting this request',
        blank=True,
        max_length=255,
        help_text="""Specify NCRIS capabilities supporting this request.""")

    allocation_home = models.CharField(
        "Allocation Home",
        choices=allocation_home_choices.ALLOC_HOME_CHOICE[1:],
        blank=True,
        null=True,
        max_length=128,
        help_text="""Allocation home of the allocation""",
    )

    provisioned = models.BooleanField(default=False)

    notes = models.TextField(
        "Private notes for admins",
        null=True, blank=True,
        help_text="These notes are only visible to allocation admins")

    notifications = models.BooleanField(
        default=True,
        help_text="Send notifications for this allocation")

    class Meta:
        ordering = ['-modified_time']

    def get_absolute_url(self):
        return reverse('horizon:allocation:requests:allocation_view',
                       args=[str(self.id)])

    def set_status(self, status):
        status = status.upper()
        status_abbreviations = [abbr for abbr, full_name in
                                self.REQUEST_STATUS_CHOICES]
        if status not in status_abbreviations:
            raise Exception()

        self.status = status

    def is_active(self):
        """Return True if the allocation has either been approved,
        false otherwise.
        """
        return self.status.lower() == 'a'

    def is_rejected(self):
        """Return True if the allocation has either been accepted or
        rejected, false otherwise.
        """
        return self.status.lower() in ('r', 'j')

    def is_requested(self):
        return self.status.lower() in ('e', 'n')

    def amendment_requested(self):
        """Return True if the user has requested an extention
        """
        return self.status.lower() in ('x', 'j')

    def is_archived(self):
        return self.parent_request is not None

    def can_be_amended(self):
        return self.is_active() and not self.is_archived()

    def can_be_extended(self):
        return self.can_be_amended() and not self.is_archived()

    def can_be_edited(self):
        return not self.is_active() and not self.is_archived()

    def can_admin_edit(self):
        return self.status.lower() not in ('p', 'a') and not self.is_archived()

    def can_user_edit(self):
        return self.status.lower() in (
            'e', 'r', 'n') and not self.is_archived()

    def can_user_edit_amendment(self):
        return self.amendment_requested() and not self.is_archived()

    def can_be_rejected(self):
        return self.is_requested() and not self.is_archived()

    def can_be_approved(self):
        return self.is_requested() and not self.is_archived()

    def can_reject_change(self):
        return self.can_approve_change()

    def can_approve_change(self):
        return self.amendment_requested() and not self.is_archived()

    def notify_via_e_mail(self, sender, recipient_list, template, cc_list=[],
                          bcc_list=[], reply_to=None):
        """Send an email to the requester notifying them that their
        allocation has been processed.
        """
        if not sender and recipient_list:
            # TODO(shauno): log this problem
            raise Exception

        plaintext = get_template(template)
        ctx = {"request": self}
        text = plaintext.render(ctx)
        subject, body = text.split('')
        email = EmailMessage(
            subject.strip(),
            body,
            sender,
            recipient_list,
            cc=cc_list
        )

        if bcc_list:
            email.bcc = bcc_list

        if reply_to:
            email.extra_headers = {'Reply-To': reply_to}

        email.send()

    def notify_user(self, template):
        to = [self.contact_email]
        cc = settings.ALLOCATION_EMAIL_RECIPIENTS
        sender = settings.ALLOCATION_EMAIL_FROM
        reply_to = settings.ALLOCATION_EMAIL_REPLY_TO
        self.notify_via_e_mail(
            template=template,
            sender=sender,
            recipient_list=to,
            cc_list=cc,
            reply_to=reply_to,
        )

    def notify_admin(self, template):
        self.notify_via_e_mail(
            sender=settings.ALLOCATION_EMAIL_FROM,
            recipient_list=settings.ALLOCATION_EMAIL_RECIPIENTS,
            template=template,
            cc_list=[self.contact_email],
            bcc_list=settings.ALLOCATION_EMAIL_BCC_RECIPIENTS,
            reply_to=settings.ALLOCATION_EMAIL_REPLY_TO,
        )

    def send_notifications(self):
        if not self.notifications:
            return
        status = self.status.lower()
        if status in ['n', 'e', 'x']:
            if status == 'n':
                template = 'rcallocation/email_alert_acknowledge.txt'
            else:
                template = 'rcallocation/email_alert.txt'
            self.notify_admin(template)
            if status == 'n':
                # N is a special state showing that the
                # request has been created but no email has
                # been sent. Progress it once it's been sent.
                self.status = 'E'
        elif self.is_rejected():
            template = 'rcallocation/email_alert_rejected.txt'
            self.notify_user(template)

    def save(self, *args, **kwargs):
        # calculate the end date based on the start date and duration
        duration_relativedelta = relativedelta(
            months=self.estimated_project_duration)
        self.end_date = self.start_date + duration_relativedelta
        if not kwargs.pop('provisioning', None):
            if not self.is_archived():
                self.modified_time = timezone.now()
                try:
                    self.send_notifications()
                except Exception:
                    LOG.error(
                        'Could not send notification email for allocation %s.'
                        % self.project_name)
                    if settings.DEBUG:
                        raise
        super(AllocationRequest, self).save(*args, **kwargs)

    def get_all_fields(self):
        """Returns a list of all non None fields, each entry containing
        the fields label, field name, and value (if the display value
        exists it is preferred)
        """
        fields = []
        for f in self._meta.fields:
            if f.editable:
                field_name = f.name

                # resolve picklists/choices, with get_xyz_display() function
                try:
                    get_choice = 'get_' + field_name + '_display'
                    if hasattr(self, get_choice):
                        value = getattr(self, get_choice)()
                    else:
                        value = getattr(self, field_name)
                except AttributeError:
                    value = None

                # only display fields with values and skip some fields entirely
                if not (value is None or field_name in ('id', 'status')):
                    fields.append(
                        {
                            'label': f.verbose_name,
                            'name': field_name,
                            'value': value,
                        }
                    )
        return fields

    def __str__(self):
        return '"{0}" {1}'.format(self.project_name, self.contact_email)


class Zone(models.Model):
    name = models.CharField(primary_key=True, max_length=32)
    display_name = models.CharField(max_length=64)

    def __str__(self):
        return self.display_name


class ServiceType(models.Model):
    catalog_name = models.CharField(primary_key=True, max_length=32)
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)
    zones = models.ManyToManyField(Zone)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    INTEGER = 'integer'
    BOOLEAN = 'boolean'
    RESOURCE_TYPES = (
        (INTEGER, 'Integer'),
        (BOOLEAN, 'Boolean'),
    )
    name = models.CharField(max_length=64)
    service_type = models.ForeignKey(ServiceType)
    quota_name = models.CharField(max_length=32)
    unit = models.CharField(max_length=32)
    requestable = models.BooleanField(default=True)
    help_text = models.TextField(null=True, blank=True)
    resource_type = models.CharField(max_length=10, blank=False,
                                     choices=RESOURCE_TYPES,
                                     default=INTEGER)

    def __str__(self):
        return self.name

    def codename(self):
        return "%s.%s" % (self.service_type.catalog_name, self.quota_name)

    class Meta:
        unique_together = ('service_type', 'quota_name')
        ordering = ['id']


class QuotaGroup(models.Model):
    allocation = models.ForeignKey(AllocationRequest, related_name='quotas')
    zone = models.ForeignKey(Zone)
    service_type = models.ForeignKey(ServiceType)

    class Meta:
        unique_together = ("allocation", "zone", "service_type")

    def __str__(self):
        return '{0} {1} {2}'.format(self.allocation.id,
                                    self.service_type, self.zone)


class Quota(models.Model):
    group = models.ForeignKey(QuotaGroup)
    resource = models.ForeignKey(Resource)
    requested_quota = models.PositiveIntegerField(
        'Requested quota',
        default='0')
    quota = models.PositiveIntegerField(
        "Allocated quota",
        default='0')

    class Meta:
        unique_together = ("group", "resource")

    def __str__(self):
        return '{0} {1} {2}'.format(self.group.allocation.id,
                                    self.resource, self.group.zone)


class ChiefInvestigator(models.Model):
    allocation = models.ForeignKey(AllocationRequest,
                                   related_name='investigators')

    title = models.CharField(
        'Title',
        blank=False,
        max_length=60,
        help_text="""The chief investigator's title"""
    )

    given_name = models.CharField(
        'Given name',
        blank=False,
        max_length=200,
        help_text="""The chief investigator's given name"""
    )

    surname = models.CharField(
        'Surname',
        blank=False,
        max_length=200,
        help_text="""The chief investigator's surname"""
    )

    email = models.EmailField(
        'Institutional email address',
        blank=False,
        help_text="""Email address must belong the university or
            organisation for accountability."""
    )

    institution = models.CharField(
        'Institution',
        blank=False,
        max_length=200,
        help_text="""The name of the institution or university of
                    the chief investigator including the schools,
                    faculty and/or department."""
    )

    additional_researchers = models.TextField(
        'Please list all other primary investigators, partner investigators '
        'and other research collaborators',
        blank=True,
        max_length=1000,
        default='',
        help_text="""Please list all other primary investigators, partner
        investigators and other research collaborators"""
    )

    def __str__(self):
        return '{0} {1} {2}'.format(self.title, self.given_name, self.surname)


class Institution(models.Model):
    name = models.CharField(
        'Supported institutions',
        max_length=200,
        help_text="""List the Australian research institutions and
                    universities supported by this application. If this
                    application is just for you, just write the name of
                    your institution or university. If you are running a
                    public web service list the Australian research
                    institutions and universities that
                    you think will benefit most.""")

    allocation = models.ForeignKey(AllocationRequest,
                                   related_name='institutions')

    class Meta:
        unique_together = ("allocation", "name")

    def __str__(self):
        return self.name


class Publication(models.Model):
    publication = models.CharField(
        'Publication/Output',
        max_length=512,
        help_text="""Please provide any traditional and non-traditional
                research outputs using a citation style text reference
                for each. eg. include article/title, journal/outlet, year,
                DOI/link if available.""")

    allocation = models.ForeignKey(AllocationRequest,
                                   related_name='publications')

    def __str__(self):
        return self.publication


class Grant(models.Model):
    grant_type = models.CharField(
        "Type",
        choices=grant_type.GRANT_TYPES,
        blank=False,
        null=False,
        default='arc',
        max_length=128,
        help_text="""Choose the grant type from the dropdown options."""
    )

    funding_body_scheme = models.CharField(
        "Funding body and scheme",
        blank=False,
        max_length=255,
        help_text="""For example, ARC Discovery Project."""
    )

    grant_id = models.CharField(
        'Grant ID',
        blank=True,
        max_length=200,
        help_text="""Specify the grant id."""
    )

    first_year_funded = models.IntegerField(
        'First year funded',
        blank=False,
        default=datetime.datetime.now().year,
        validators=[MinValueValidator(1970), MaxValueValidator(3000)],
        error_messages={
            'min_value': 'Please input a year between 1970 ~ 3000',
            'max_value': 'Please input a year between 1970 ~ 3000'},
        help_text="""Specify the first year funded"""
    )

    last_year_funded = models.IntegerField(
        'Last year funded',
        blank=False,
        default=datetime.datetime.now().year + 1,
        validators=[MinValueValidator(1970), MaxValueValidator(3000)],
        error_messages={
            'min_value': 'Please input a year between 1970 ~ 3000',
            'max_value': 'Please input a year between 1970 ~ 3000'},
        help_text="""Specify the last year funded"""
    )

    total_funding = models.FloatField(
        'Total funding (AUD)',
        validators=[MinValueValidator(1)],
        help_text="""Total funding amount in AUD"""
    )

    allocation = models.ForeignKey(AllocationRequest, related_name='grants')

    class Meta:
        unique_together = ("allocation", "grant_type", "funding_body_scheme",
                           "grant_id", "first_year_funded", "total_funding")

    def __str__(self):
        return "Funding : {0} , total funding: {1}".format(
            self.funding_body_scheme, self.total_funding)
