import logging

from rcportal.rcallocation.models import AllocationRequest
from rcportal.rcallocation.views import AllocationsListView

LOG = logging.getLogger('rcportal.rcallocation')


class ApprovedAllocationsListView(AllocationsListView):
    def get_data(self):
        return [ar for ar in
                AllocationRequest.objects.filter(
                    parent_request=None).filter(
                    status__in=('A', 'X')).order_by(
                    'project_name').prefetch_related(
                    'quotas', 'investigators', 'institutions',
                    'publications', 'grants')]
