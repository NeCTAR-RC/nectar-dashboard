from horizon import tables

from nectar_dashboard.rcallocation.tables import BaseAllocationListTable
from nectar_dashboard.rcallocation.tables import EditRequest
from nectar_dashboard.rcallocation.tables import ViewHistory


class ApprovedEditRequest(EditRequest):
    url = "horizon:allocation:approved_requests:edit_request"


class ApprovedAllocationListTable(BaseAllocationListTable):
    class Meta:
        verbose_name = "Approved Requests"
        table_actions = (tables.NameFilterAction,)
        row_actions = (ViewHistory, ApprovedEditRequest)

    def __init__(self, *args, **kwargs):
        super(ApprovedAllocationListTable, self).__init__(*args, **kwargs)
