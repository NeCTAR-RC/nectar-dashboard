from horizon import tables

from nectar_dashboard.rcallocation.tables import BaseAllocationListTable
from nectar_dashboard.rcallocation.tables import EditRequest
from nectar_dashboard.rcallocation.tables import ViewHistory


class PendingAllocationListTable(BaseAllocationListTable):

    approver = tables.Column('approver_email',
                             verbose_name='Previous Approver')
    submit_date = tables.Column('submit_date',
                                verbose_name='Submitted Date')

    def __init__(self, *args, **kwargs):
        super(PendingAllocationListTable, self).__init__(*args, **kwargs)
        self.columns.pop('end_date')

    class Meta:
        verbose_name = "Pending Requests"
        table_actions = (tables.NameFilterAction,)
        row_actions = (EditRequest, ViewHistory,)
