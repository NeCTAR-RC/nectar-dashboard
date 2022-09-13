import datetime

from django.db.models import Q
from horizon import tables as horizon_tables
from horizon.utils import memoized

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import tables
from nectar_dashboard.rcallocation import utils


# These correspond to expiration states for expiring allocations
DANGER = 'Danger'      # getting close to auto-decline
ARCHIVED = 'Archived'
STOPPED = 'Stopped'
EXPIRED = 'Expired'
UNKNOWN = 'Unknown'    # can't figure out when the expiry clock stopped.

# These represent the waiting time for non-expiring allocations
OVERDUE = 'Overdue'
WARNING = 'Warning'
ATTENTION = 'Attention'
NEW = 'New'

APPROVED = models.AllocationRequest.APPROVED
UPDATE_PENDING = models.AllocationRequest.UPDATE_PENDING


@memoized.memoized
def get_ardc_site():
    return models.Site.objects.get(name='ardc')


def _dummy(dummy):
    pass


def get_highlight_attribute(data):
    '''Map an urgency string to a CSS class name for a color.
    '''

    if data[0] == '(':
        return {}
    if data == DANGER:
        css_class = 'pending_warn_level_4'
    elif data in (STOPPED, ARCHIVED, EXPIRED, OVERDUE, UNKNOWN):
        css_class = 'pending_warn_level_3'
    elif data == WARNING:
        css_class = 'pending_warn_level_2'
    elif data == OVERDUE:
        css_class = 'pending_warn_level_1'
    else:
        css_class = 'pending_warn_level_0'
    return {'class': css_class}


def get_clockstop_amendment(allocation):
    '''Gets the amendment request that we infer would have stopped the
    expiry clock for this allocation's current expiration.  This does
    not take account of ticket holds or the special Christmas break logic.
    There is also a scenario where an amendment is declined but the user
    then submits a further amendment.  In that scenario, it is unclear
    what the notional "clock stop" time should be.

    These edge-cases could be avoided by querying Keystone (indirectly)
    to find out the project's real expiry status.
    '''

    # The last approved allocation
    approval = models.AllocationRequest.objects \
                                       .filter(status=APPROVED) \
                                       .filter(parent_request=allocation.id) \
                                       .first()
    if approval is None:
        return None
    # The first amendment after the last approval
    return models.AllocationRequest.objects \
                                   .filter(status=UPDATE_PENDING) \
                                   .filter(Q(parent_request=allocation.id)
                                           | Q(id=allocation.id)) \
                                   .filter(modified_time__gt=
                                           approval.modified_time) \
                                   .order_by('modified_time') \
                                   .first()


def get_urgency(allocation):
    '''Derive the urgency for the urgency field from the modification
    date for the current allocation request and the project's inferred
    expiration state ... if the allocation past its end date.  This does not
    take account of ticket holds.  (That would require a Keystone "project
    show" and the Approver doesn't have permission to do that.)
    '''

    today = datetime.date.today()
    mod_date = allocation.modified_time.date()
    urgency = None
    if allocation.end_date and allocation.end_date < datetime.date.today():
        # Allocations that are expiring.  The urgency corresponds to
        # the expiry state at the point that we infer that the expiry
        # clock was stopped.
        clockstop = get_clockstop_amendment(allocation)
        if clockstop:
            expiry_clock = clockstop.modified_time.date()
            if expiry_clock + datetime.timedelta(days=30 * 5) < today:
                # At risk of automatic decline, restarting expiry
                urgency = DANGER
            elif expiry_clock > allocation.end_date + datetime.timedelta(
                    days=28):
                urgency = ARCHIVED
            elif expiry_clock > allocation.end_date + datetime.timedelta(
                    days=14):
                urgency = STOPPED
            elif expiry_clock > allocation.end_date:
                urgency = EXPIRED
        else:
            urgency = UNKNOWN
    if urgency is None:
        if mod_date + datetime.timedelta(days=21) < today:
            # Approval SLA is 2 to 3 weeks.  Past 3 weeks
            urgency = OVERDUE
        elif mod_date + datetime.timedelta(days=14) < today:
            # Approval SLA is 2 to 3 weeks.  In that range
            urgency = WARNING
        elif mod_date + datetime.timedelta(days=7) < today:
            # Getting warm ...
            urgency = ATTENTION
        else:
            urgency = NEW
    return urgency


class UrgencyColumn(horizon_tables.Column):
    # It would be nice if we could implement this using a 'transform'
    # callable ... but the transform callable can't get access to the
    # request to find out who the approver is.

    def __init__(self):
        super().__init__(_dummy, verbose_name='Urgency',
                       cell_attributes_getter=get_highlight_attribute)

    def get_raw_data(self, allocation):
        urgency = get_urgency(allocation)

        # Determine (heuristically) if this request is relevant
        # to the approver.  Did their site approve it last time?
        # Does the contact email map to an org affiliated with
        # their site?  If neither ... are they an ARDC approver?
        username = self.table.request.user.username
        approver_sites = models.Site.objects.get_by_approver(username)
        if allocation.associated_site:
            alloc_sites = [allocation.associated_site]
        else:
            alloc_sites = utils.sites_from_email(allocation.contact_email)
            if len(alloc_sites) == 0:
                alloc_sites = [get_ardc_site()]
        common_sites = [s for s in alloc_sites if s in approver_sites]
        if len(common_sites) == 0:
            # Indicate "not relevant" with parentheses.  Note that the
            # parentheses are used when selecting the CSS class above.
            urgency = f"({urgency})"
        return urgency


class PendingAllocationListTable(tables.BaseAllocationListTable):
    class Meta:
        verbose_name = "Pending Requests"
        table_actions = (horizon_tables.NameFilterAction,)
        row_actions = (tables.EditRequest, tables.ViewHistory,)

    approver = horizon_tables.Column('approver_email',
                                     verbose_name='Previous Approver')
    urgency = UrgencyColumn()
