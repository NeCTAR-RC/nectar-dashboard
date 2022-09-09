from horizon import tables as horizon_tables
from horizon.utils import memoized

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import tables
from nectar_dashboard.rcallocation import urgency


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
    if data == urgency.DANGER:
        css_class = 'pending_warn_level_4'
    elif data in (urgency.STOPPED, urgency.ARCHIVED, urgency.EXPIRED,
                  urgency.OVERDUE, urgency.UNKNOWN):
        css_class = 'pending_warn_level_3'
    elif data == urgency.WARNING:
        css_class = 'pending_warn_level_2'
    elif data == urgency.OVERDUE:
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
        urgency_value = urgency.get_urgency(allocation)

        # Determine (heuristically) if this request is relevant
        # to the approver.  Did their site approve it last time?
        # Does the contact email map to an org affiliated with
        # their site?  If neither ... are they an ARDC approver?
        username = self.table.request.user.username
        approver_sites = models.Site.objects.get_by_approver(username)
        interested_sites = allocation.get_interested_sites()
        if len(interested_sites) == 0:
            # If an allocation's related sites cannot be determined,
            # its for ARDC to triage.
            interested_sites = [get_ardc_site()]
        common_sites = [s for s in interested_sites if s in approver_sites]
        if len(common_sites) == 0:
            # Indicate "not relevant" with parentheses.  Note that the
            # parentheses are used when selecting the CSS class above.
            urgency_value = f"({urgency_value})"
        return urgency_value


class PendingAllocationListTable(tables.BaseAllocationListTable):
    class Meta:
        verbose_name = "Pending Requests"
        table_actions = (horizon_tables.NameFilterAction,)
        row_actions = (tables.EditRequest, tables.ViewHistory,)

    approver = horizon_tables.Column('approver_email',
                                     verbose_name='Previous Approver')
    urgency = UrgencyColumn()
