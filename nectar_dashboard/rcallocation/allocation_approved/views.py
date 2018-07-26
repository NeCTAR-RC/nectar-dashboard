import logging

from nectar_dashboard.rcallocation.models import AllocationRequest
from nectar_dashboard.rcallocation.views import AllocationsListView

LOG = logging.getLogger('nectar_dashboard.rcallocation')


class ApprovedAllocationsListView(AllocationsListView):
    page_title = 'Approved Requests'
    def get_data(self):
        return [ar for ar in
                AllocationRequest.objects.filter(
                    parent_request=None).filter(
                    source=AllocationRequest.WEB).filter(
                    status__in=('A', 'X', 'J')).order_by(
                        'project_name').prefetch_related(
                            'quotas', 'investigators', 'institutions',
                            'publications', 'grants')]
