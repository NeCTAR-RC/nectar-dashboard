from horizon.utils import memoized

from nectar_dashboard.api import usage
from nectar_dashboard.rcallocation import models


@memoized.memoized
def get_current_allocation(request):
    allocations = models.AllocationRequest.objects \
        .filter(project_id=request.user.project_id) \
        .filter(status=models.AllocationRequest.APPROVED)

    if allocations:
        return allocations[0]


@memoized.memoized
def get_quota(request, resource_code):
    allocation = get_current_allocation(request)
    if allocation is None:
        return None

    resource = models.Reseource.objects.get_by_codename(resource_code)
    quota = models.Quota.objects.get(group__allocation=allocation,
                                     resource=resource)

    if quota:
        return quota.quota


@memoized.memoized
def get_usage(request):
    allocation = get_current_allocation(request)
    if allocation is None:
        return None

    begin = allocation.start_date.strftime('%Y-%m-%d')
    end = allocation.end_date.strftime('%Y-%m-%d')
    usage_data = usage.get_summary(request, resource_type='instance',
                                   begin=begin, end=end)

    return usage_data
