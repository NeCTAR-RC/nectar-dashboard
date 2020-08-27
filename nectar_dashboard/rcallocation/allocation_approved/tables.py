from horizon import tables

from nectar_dashboard.rcallocation.tables import BaseAllocationListTable
from nectar_dashboard.rcallocation.tables import ViewHistory


class ApprovedAllocationListTable(BaseAllocationListTable):
    class Meta:
        verbose_name = "Approved Requests"
        table_actions = (tables.NameFilterAction,)
        row_actions = (ViewHistory,)
