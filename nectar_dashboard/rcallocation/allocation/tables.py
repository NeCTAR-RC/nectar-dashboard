from horizon import tables

from nectar_dashboard.rcallocation.tables import BaseAllocationListTable
from nectar_dashboard.rcallocation.tables import EditRequest
from nectar_dashboard.rcallocation.tables import ViewHistory


class PendingAllocationListTable(BaseAllocationListTable):
    class Meta:
        verbose_name = "Pending Requests"
        table_actions = (tables.NameFilterAction,)
        row_actions = (EditRequest, ViewHistory,)

    approver = tables.Column('approver_email',
                             verbose_name='Previous Approver')
