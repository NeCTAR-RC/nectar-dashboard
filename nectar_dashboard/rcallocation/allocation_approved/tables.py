from horizon import tables

from nectar_dashboard.rcallocation.tables import BaseAllocationListTable
from nectar_dashboard.rcallocation.tables import ViewHistory


class ApprovedAllocationListTable(BaseAllocationListTable):
    class Meta:
        verbose_name = "Approved Requests"
        table_actions = (tables.NameFilterAction,)
        row_actions = (ViewHistory,)

    def __init__(self, *args, **kwargs):
        super(BaseAllocationListTable, self).__init__(*args, **kwargs)
        self.columns.pop('requested_home')
