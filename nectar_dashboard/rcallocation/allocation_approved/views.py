import logging

from nectar_dashboard.rcallocation.allocation_approved import tables
from nectar_dashboard.rcallocation.models import AllocationRequest
from nectar_dashboard.rcallocation.views import BaseAllocationsListView


LOG = logging.getLogger('nectar_dashboard.rcallocation')


class ApprovedAllocationsListView(BaseAllocationsListView):
    page_title = 'Approved Requests'
    table_class = tables.ApprovedAllocationListTable

    def get_data(self):
        return [
            ar
            for ar in AllocationRequest.objects.filter(parent_request=None)
            .filter(status__in=('A', 'X', 'J'))
            .order_by('project_name')
        ]
