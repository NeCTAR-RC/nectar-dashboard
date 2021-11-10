# Models for the ResearchCloud Allocations portal
# Original: Tom Fifield <fifieldt@unimelb.edu.au> - 2011-10
# Modified by Martin Paulo
import datetime
import logging
import re

from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse

from nectar_dashboard.rcallocation import forcodes
from nectar_dashboard.rcallocation import grant_type as nectar_grant_type
from nectar_dashboard.rcallocation import output_type_choices
from nectar_dashboard.rcallocation import project_duration_choices

from nectar_dashboard.rcallocation.notifier import create_notifier

LOG = logging.getLogger(__name__)


#############################################################################
#
# Requests are created by Users who wish to receive Allocations
#
#############################################################################


def _six_months_from_now():
    return datetime.date.today() + datetime.timedelta(
        days=30 * 6)


class UsageType(models.Model):
    name = models.CharField('Usage Type', max_length=40)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class NCRISFacility(models.Model):
    name = models.CharField(
        'Full NCRIS facility name', max_length=200, unique=True)

    short_name = models.CharField(
        'Common short name or acronym', max_length=200, unique=True)

    def __str__(self):
        return self.short_name


class ARDCSupport(models.Model):
    name = models.CharField(
        'Full ARDC program or project name', max_length=200, unique=True)

    short_name = models.CharField(
        'Common short name or acronym', max_length=200, unique=True)

    project = models.BooleanField(
        'Distinguishes projects from programs',
        default=True,
        help_text='True for projects, false for programs')

    project_id = models.CharField(
        'ARDC project ID',
        blank=True,
        max_length=20)

    enabled = models.BooleanField(
        'Determines if the user can choose this program or project',
        default=True,
        help_text='False hides the program or project')

    # Used by the allocation form to order these objects in a select
    # widget, if they have the same value they will be grouped together
    # using optgroups.
    rank = models.IntegerField(
        'Determines the primary ranking in menus',
        default=100,
        help_text='Smaller values mean earlier.  Duplicates are OK.')

    explain = models.BooleanField(
        'Determines if this program or project requires more details',
        default=False,
        help_text='When true, the ARDC Support Details field '
        'should provide details.  This is typically used for programs '
        'rather than projects')

    def __str__(self):
        return self.short_name


class AllocationRequest(models.Model):
    """An AllocationRequest represents a point in time in the history of
    a Nectar allocation.  The history is represented by the parent request
    chain.  When a significant change is made.  The id (pk) of the most
    recent AllocationRequest record for an allocation should remain the
    same.
    """

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
                                       blank=True, on_delete=models.SET_NULL)

    status = models.CharField(max_length=1,
                              choices=REQUEST_STATUS_CHOICES,
                              default=SUBMITTED)

    status_explanation = models.TextField(
        null=True, blank=True,
        verbose_name="Reason",
        help_text="A brief explanation of the reason the request has been "
                  "sent back to the user for changes")

    created_by = models.CharField(max_length=100)

    submit_date = models.DateTimeField('Submission Date',
                                       auto_now_add=True)

    modified_time = models.DateTimeField('Modified Date', auto_now=True)

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
        null=True,
        help_text='The day when the allocation starts')

    end_date = models.DateField(
        'End date',
        null=True,
        help_text='The day when the allocation ends.')

    estimated_project_duration = models.IntegerField(
        'Estimated project duration',
        choices=project_duration_choices.DURATION_CHOICE,
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
        "Research project description",
        max_length=4096,
        help_text='This section should provide a brief overview of the '
                  'Research Project or Projects that the requested '
                  'allocation would directly support. We will use this '
                  'information to help prioritize the allocation of '
                  'resources to different projects.')

    usage_patterns = models.TextField(
        "Justification and details of your Proposed Cloud Usage",
        max_length=1024, blank=True,
        help_text='Explain why you need Nectar Research Cloud resources, '
                  'and how they will be used to support your research. '
                  'Include relevant technical information on your proposed '
                  'use of the resources; e.g. software applications, '
                  'characteristics of computational tasks, data quantities '
                  'and access patterns, frequency and intensity of '
                  'utilization, and so on.  We will use this information '
                  'to help us decide if the resources that you are '
                  'requesting are appropriate to the tasks to be performed.')

    geographic_requirements = models.TextField(
        max_length=1024,
        blank=True,
        verbose_name="Special location requirements",
        help_text="""Indicate to the allocations committee any special
                geographic requirements that you may need; e.g. to run
                at a specific node or at multiple nodes.  Please
                include your reasons for these requirements.""")

    project_id = models.CharField(max_length=36, blank=True, null=True)

    estimated_number_users = models.IntegerField(
        'Estimated number of users',
        default='1',
        validators=[MinValueValidator(1), ],
        error_messages={
            'min_value': 'The estimated number of users must be great than 0'},
        help_text="""Estimated number of users, researchers and collaborators
        to be supported by the allocation.""")

    FOR_CHOICES = tuple((k, "%s %s" % (k, v))
                        for k, v in forcodes.FOR_CODES.items())
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

    # Legacy: remove when the ardc_support relation is populated
    # for all current and historical allocation records.  Until then
    # don't allow it to be entered, and hide it if the allocation
    # record has any related ARDCSupport records.
    nectar_support = models.CharField(
        """List any ARDC (or ANDS, Nectar, or RDS) funded projects
        supporting this request.""",
        blank=True,
        max_length=255,
        help_text="""List any ongoing projects that 1) are or were
        funded by ARDC or its predecessors (ANDS, Nectar, or RDS),
        and 2) where the project's management supports this request
        in furtherance of its goals, and 3) where this allocation
        will provide resources that benefit the project.""")

    ardc_support = models.ManyToManyField(ARDCSupport, blank=True)

    ardc_explanation = models.CharField(
        'ARDC Support details',
        blank=True,
        max_length=1024,
        help_text="""You can use this field to provide extra details for
        the ARDC project(s) supporting this request.""")

    # Legacy: remove when the ncris_facility relation is populated
    # for all current and historical allocation records.  Until then
    # don't allow it to be entered, and hide it if the allocation
    # record has any related NCRISFacility records.
    ncris_support = models.CharField(
        'List NCRIS capabilities supporting this request',
        blank=True,
        max_length=255,
        help_text="""List any NCRIS facilities where the facility
        management supports this request in furtherance of its goals.
        For example, the requested resources may enable a project
        that the NCRIS facility is funding, or they may enable the
        provision of infrastructure for the facility.""")

    ncris_explanation = models.CharField(
        'NCRIS Support details',
        blank=True,
        max_length=1024,
        help_text="""You can use this field to provide extra details for
        the NCRIS Facility(s) supporting or supported by this request.""")

    ncris_facilities = models.ManyToManyField(NCRISFacility, blank=True)

    associated_site = models.ForeignKey(
        'Site',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text="""The Nectar site that is primarily associated
        with this allocation.  Under normal circumstances, this will
        be the site whose approver has most recently approved the
        allocation""",
    )

    national = models.BooleanField(
        "National funding",
        default=False,
        help_text="""If true, this indicates that the allocation
        was most recently assessed as meeting the criteria for Nectar
        National funding""")

    special_approval = models.CharField(
        "Special RC-NAS approval reasons",
        blank=True,
        max_length=1024,
        help_text="""Use this field to record reasons the allocation
        is approved as National despite not meeting the primary criteria;
        i.e. a current competitive, NCRIS support or ARDC support.
        See the RC-NAS policy for the possible reasons.  This is only
        visible to allocation admins""")

    provisioned = models.BooleanField(default=False)

    notes = models.TextField(
        "Private notes for admins",
        null=True, blank=True,
        help_text="These notes are only visible to allocation admins")

    notifications = models.BooleanField(
        default=True,
        help_text="Send notifications for this allocation")

    managed = models.BooleanField(
        default=True,
        help_text="Whether the allocation is managed through the dashboard")

    usage_types = models.ManyToManyField(UsageType)

    class Meta:
        ordering = ['-modified_time']

    @property
    def allocation_home(self):
        if self.national:
            return 'national'
        elif not self.associated_site:
            return 'unassigned'
        else:
            return self.associated_site.name

    @property
    def allocation_home_display(self):
        if self.national:
            return 'National'
        elif not self.associated_site:
            return 'Unassigned'
        else:
            return self.associated_site.display_name

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
        return self.status.upper() == self.APPROVED

    def is_rejected(self):
        """Return True if the allocation has either been accepted or
        rejected, false otherwise.
        """
        return self.status.upper() in (self.DECLINED, self.UPDATE_DECLINED)

    def is_requested(self):
        return self.status.upper() in (self.SUBMITTED, self.NEW)

    def amendment_requested(self):
        """Return True if the user has requested an extention
        """
        return self.status.upper() in (self.UPDATE_PENDING,
                                       self.UPDATE_DECLINED)

    def is_history(self):
        return self.parent_request is not None

    def can_be_amended(self):
        return self.is_active() and not self.is_history() and self.managed

    def can_be_edited(self):
        return not self.is_active() and not self.is_history() and self.managed

    def can_admin_edit(self):
        return self.status.upper() != self.APPROVED \
            and not self.is_history() and self.managed

    def can_user_edit(self):
        return self.status.upper() in (self.SUBMITTED, self.DECLINED,
                                       self.NEW) \
            and not self.is_history() and self.managed

    def can_user_edit_amendment(self):
        return self.amendment_requested() and not self.is_history() \
            and self.managed

    def can_be_rejected(self):
        return self.is_requested() and not self.is_history() and self.managed

    def can_be_approved(self):
        return self.is_requested() and not self.is_history() and self.managed

    def can_reject_change(self):
        return self.can_approve_change()

    def can_approve_change(self):
        return self.amendment_requested() and not self.is_history()

    def can_have_publications(self):
        return self.status.upper() not in (self.SUBMITTED, self.DECLINED,
                                           self.NEW)

    def get_quotas_context(self):
        quotas = []
        for quota in Quota.objects.filter(group__allocation=self):
            quotas.append({'service_type': quota.group.service_type.name,
                           'resource': quota.resource.name,
                           'resource_type': quota.resource.resource_type,
                           'unit': quota.resource.unit,
                           'zone': quota.group.zone.display_name,
                           'quota': quota.quota,
                           'requested_quota': quota.requested_quota})
        return quotas

    def send_email_notification(self, template, extra_context={}):
        if not self.notifications:
            return

        notifier = create_notifier(self)

        # Select the template
        format = 'html' if notifier.expects_html else 'txt'
        template_name = f"rcallocation/email_{template}.{format}"

        # Prepare context for template rendering
        context = extra_context.copy()
        context['allocation'] = self
        context['quotas'] = self.get_quotas_context()
        ar_previous = AllocationRequest.objects.filter(
            parent_request=self, provisioned=True).first()
        if ar_previous:
            context['quotas_previous'] = ar_previous.get_quotas_context()
        context['base_url'] = 'https://dashboard.rc.nectar.org.au'
        if 'request' in context:
            context['base_url'] = '{}://{}'.format(
                context['request'].scheme, context['request'].get_host())

        # Render template, separate body and subject, and send email
        text = render_to_string(template_name, context)
        subject, _, body = text.partition('\n\n')
        notifier.send_email(email=self.contact_email,
                            subject=subject,
                            body=body)

    def send_notifications(self, extra_context={}):
        if self.status in [self.NEW, self.SUBMITTED, self.UPDATE_PENDING]:
            if self.status == self.NEW:
                template = 'alert_acknowledge'
            else:
                template = 'alert'
            self.send_email_notification(template, extra_context=extra_context)
            if self.status == self.NEW:
                # N is a special state showing that the
                # request has been created but no email has
                # been sent. Progress it once it's been sent.
                self.status = self.SUBMITTED
                self.save()
        elif self.is_rejected():
            template = 'alert_rejected'
            self.send_email_notification(template, extra_context=extra_context)

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

    def save_without_updating_timestamps(self):
        """Saves this AllocationRequest without auto-updating the timestamps.
        Note that if you do this when the 'submit_date' is None, you may get
        DB constraint violation, 'cos there is currently a not null constraint
        on the field.
        """
        manager = AllocationRequest.objects
        saved_modified_time = self.modified_time
        saved_submit_date = self.submit_date

        # Save does the 'auto_*' updates
        self.save()

        # Reverse the effect of the 'auto_*' updates in the DB
        manager.filter(id=self.id).update(modified_time=saved_modified_time)
        manager.filter(id=self.id).update(submit_date=saved_submit_date)

        # ... and reset the values in 'self'
        self.modified_time = saved_modified_time
        self.submit_date = saved_submit_date

    def __str__(self):
        return '"{0}" {1}'.format(self.project_name, self.contact_email)


class Site(models.Model):
    """A Site represents site in the Nectar federation that the allocation
    system knows about.
    """

    name = models.CharField(unique=True, max_length=32)
    display_name = models.CharField(max_length=64)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class Approver(models.Model):
    """An Approver is a person who is authorized to approve local
    or national allocations for or on behalf of a Site.  An
    approver may be authorized to approve for multiple sites.
    This information is "advisory"; i.e. it is used to warn an
    approver if they are about to make decisions that require
    another site's authority.

    This represents the current state only.  It is not avisable
    to attempt to use it to determine which Site has approved
    an allocation request.
    """

    username = models.EmailField(unique=True)
    display_name = models.CharField(max_length=64)
    sites = models.ManyToManyField(Site)

    def __str__(self):
        return self.display_name


class Zone(models.Model):
    """A Zone represents a resource pool in which quotas may be set.
    There is a distinguished Zone ("nectar") for resources or capabilities
    that are deemed to be global / Nectar-wide.

    The relationship between these zones and nova "availability zones"
    is not necessarily 1-to-1, even discounting the "nectar" zone.
    """

    name = models.CharField(primary_key=True, max_length=32)
    display_name = models.CharField(max_length=64)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class ServiceType(models.Model):
    """A ServiceType is a group of related Resources provided by a
    logical service.  For example the "Compute" service type groups
    the instance count and VCPU count resources and the resources that
    represent the permission to launch memory and cpu-intensive flavors.
    """

    catalog_name = models.CharField(primary_key=True, max_length=32)
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)
    zones = models.ManyToManyField(Zone)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    """A Resource represents a resource or capability that is controlled
    / rationed by way of quotas.  Resources that are numerically quantifiable
    have resource type "integer" and unit; e.g RAM is measured in gigabytes.
    Resources that represent a capability have a resource type "boolean".
    """

    INTEGER = 'integer'
    BOOLEAN = 'boolean'
    RESOURCE_TYPES = (
        (INTEGER, 'Integer'),
        (BOOLEAN, 'Boolean'),
    )
    name = models.CharField(max_length=64)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    quota_name = models.CharField(max_length=32)
    unit = models.CharField(max_length=32)
    requestable = models.BooleanField(default=True)
    help_text = models.TextField(null=True, blank=True)
    resource_type = models.CharField(max_length=10,
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
    """A QuotaGroup object relates a group of Quotas (for resources in
    one ServiceType) to a Zone and an AllocationRequest.
    """

    allocation = models.ForeignKey(AllocationRequest, related_name='quotas',
                                   on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("allocation", "zone", "service_type")

    def __str__(self):
        return '{0} {1} {2}'.format(self.allocation.id,
                                    self.service_type, self.zone)


class Quota(models.Model):
    """A Quota object represent the actual value for a given Resource
    for a particular allocation.  (The relation to the allocation is
    via the QuotaGroup.)
    """

    group = models.ForeignKey(QuotaGroup, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    requested_quota = models.IntegerField(
        'Requested quota',
        default='0',
        validators=[MinValueValidator(-1)])
    quota = models.IntegerField(
        "Allocated quota",
        default='0',
        validators=[MinValueValidator(-1)])

    class Meta:
        unique_together = ("group", "resource")

    def __str__(self):
        return '{0} {1} {2}'.format(self.group.allocation.id,
                                    self.resource, self.group.zone)


class ChiefInvestigator(models.Model):
    allocation = models.ForeignKey(AllocationRequest,
                                   related_name='investigators',
                                   on_delete=models.CASCADE)

    title = models.CharField(
        'Title',
        max_length=60,
        help_text="""The chief investigator's title"""
    )

    given_name = models.CharField(
        'Given name',
        max_length=200,
        help_text="""The chief investigator's given name"""
    )

    surname = models.CharField(
        'Surname',
        max_length=200,
        help_text="""The chief investigator's surname"""
    )

    email = models.EmailField(
        'Institutional email address',
        help_text="""Email address must belong the university or
            organisation for accountability."""
    )

    institution = models.CharField(
        'Institution',
        max_length=200,
        help_text="""The name of the institution or university of
                    the chief investigator including the schools,
                    faculty and/or department."""
    )

    additional_researchers = models.TextField(
        'Please list all other primary investigators, partner investigators '
        'and other research collaborators',
        max_length=1000,
        blank=True,
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
                                   related_name='institutions',
                                   on_delete=models.CASCADE)

    class Meta:
        unique_together = ("allocation", "name")

    def __str__(self):
        return self.name


DOI_PATTERN = re.compile("^10.\\d{4,9}/[^\x00-\x1f\x7f-\x9f\\s]+$")
VALIDATE_DOI = RegexValidator(regex=DOI_PATTERN,
                              message="""Invalid DOI.  A DOI looks like
                                      '10.<digits>/<characters>' with
                                      the restriction that there are no
                                      whitespace or control chars in
                                      <characters>""")
OUTPUT_TYPE_CHOICES = ((None, "Select an output type"),) \
                      + output_type_choices.OUTPUT_TYPE_CHOICE


class Publication(models.Model):
    # Only 'Peer reviewed journal article' (AJ) pubs need to be reported
    # to NCRIS.  Unspecified (U) should not be used in new publications
    output_type = models.CharField(
        'Research Output type',
        choices=OUTPUT_TYPE_CHOICES,
        max_length=2,
        help_text="""Select a publication type that best describes
                the publication.  The 'Media publication' type is
                intended to encompass traditional media and 'new'
                media such as websites, blogs and social media.""")

    publication = models.CharField(
        'Details of Research Output',
        max_length=512,
        help_text="""Provide details of the Research Output according to its
                type.  For example a Paper or Book's citation, a Dataset's
                title and URI, Software product's name and website URL,
                a Patent's title and number.  This field should not be
                used for Research Outputs with DOIs known to CrossRef.""",
        blank=True)

    # Required for 'AJ' publications for NCRIS
    doi = models.CharField(
        "Digital Object Identifier (DOI)",
        validators=[VALIDATE_DOI],
        max_length=256,
        help_text="""Provide the Research Output's DOI.  A DOI should be
               provided for all books and peer-reviewed papers.  A valid
               DOI starts with '10.&lt;number&gt;/'.  This is followed by
               letters, numbers and other characters.  For example:
               '10.23456/abc-123'.""",
        blank=True,
        default='')

    # Cached results of a CrossRef lookup for the DOI.  JSON.  This will
    # be the source for the rendering the publication details.
    crossref_metadata = models.TextField(blank=True)

    allocation = models.ForeignKey(AllocationRequest,
                                   related_name='publications',
                                   on_delete=models.CASCADE)

    def __str__(self):
        return self.publication


GRANT_TYPE_CHOICES = ((None, "Select a grant type"),) \
                     + nectar_grant_type.GRANT_TYPES
GRANT_SUBTYPE_CHOICES = ((None, "Select a grant subtype"),) \
                        + nectar_grant_type.GRANT_SUBTYPES


class Grant(models.Model):
    grant_type = models.CharField(
        "Grant Type",
        choices=GRANT_TYPE_CHOICES,
        max_length=128,
        help_text="""Choose the grant type from the dropdown options."""
    )

    grant_subtype = models.CharField(
        "Grant Subtype",
        choices=GRANT_SUBTYPE_CHOICES,
        max_length=128,
        help_text="""Choose an applicable grant subtype from the
                  dropdown options.  If no option is applicable,
                  choose 'unspecified' and then fill in the 'Other
                  funding source details' field below."""
    )

    funding_body_scheme = models.CharField(
        "Other funding source details",
        blank=True,
        max_length=255,
        help_text="""For example, details of a state government
                  grant scheme, or an industry funding source."""
    )

    grant_id = models.CharField(
        'Grant ID',
        blank=True,
        max_length=200,
        help_text="""Specify the grant id."""
    )

    first_year_funded = models.IntegerField(
        'First year funded',
        validators=[MinValueValidator(1970), MaxValueValidator(3000)],
        error_messages={
            'min_value': 'Please input a year between 1970 ~ 3000',
            'max_value': 'Please input a year between 1970 ~ 3000'},
        help_text="""Specify the first year funded"""
    )

    last_year_funded = models.IntegerField(
        'Last year funded',
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

    allocation = models.ForeignKey(AllocationRequest, related_name='grants',
                                   on_delete=models.CASCADE)

    class Meta:
        unique_together = ("allocation", "grant_type",
                           "grant_subtype", "funding_body_scheme",
                           "grant_id", "first_year_funded", "total_funding")

    def __str__(self):
        return "Funding : {0} , total funding: {1}".format(
            self.funding_body_scheme, self.total_funding)
