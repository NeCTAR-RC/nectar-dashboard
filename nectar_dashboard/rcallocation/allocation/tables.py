import datetime

from horizon import tables as horizon_tables
from horizon.utils import memoized

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import tables
from nectar_dashboard.rcallocation import utils


DANGER = 'Danger'
ARCHIVED = 'Archived'
STOPPED = 'Stopped'
EXPIRED = 'Expired'
OVERDUE = 'Overdue'
WARNING = 'Warning'
ATTENTION = 'Attention'
NEW = 'New'


@memoized.memoized
def get_ardc_site():
    return models.Site.objects.get(name='ardc')


def _dummy(dummy):
    pass


def get_highlight_attribute(data):
    if data[0] == '(':
        return {}
    if data == DANGER:
        css_class = 'pending_warn_level_4'
    elif data in (STOPPED, ARCHIVED, EXPIRED, OVERDUE):
        css_class = 'pending_warn_level_3'
    elif data == WARNING:
        css_class = 'pending_warn_level_2'
    elif data == OVERDUE:
        css_class = 'pending_warn_level_1'
    else:
        css_class = 'pending_warn_level_0'
    return {'class': css_class}


class UrgencyColumn(horizon_tables.Column):
    # It would be nice if we could implement this using a 'transform'
    # callable ... but the transform callable can't get access to the
    # request to find out who the approver is.

    def __init__(self):
        super().__init__(_dummy, verbose_name='Urgency',
                       cell_attributes_getter=get_highlight_attribute)

    def get_raw_data(self, allocation):
        today = datetime.date.today()
        mod_date = allocation.modified_time.date()
        if allocation.end_date and allocation.end_date < datetime.date.today():
            # Allocations that are expiring.  Note that the 'urgency' values
            # represent the expiry state of the allocation if it hadn't
            # been placed on hold by >this< request.  Figuring out the actual
            # state would entail a Keystone request or some gnarly analysis
            # of history records.
            if mod_date + datetime.timedelta(days=30 * 5) < today:
                # At risk of automatic decline, restarting expiry
                urgency = DANGER
            elif allocation.end_date + datetime.timedelta(days=28) < today:
                urgency = ARCHIVED
            elif allocation.end_date + datetime.timedelta(days=14) < today:
                urgency = STOPPED
            else:
                urgency = EXPIRED
        elif mod_date + datetime.timedelta(days=21) < today:
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
        if urgency:
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
                # Indicate "not relevant" with parentheses.  Note: the
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
