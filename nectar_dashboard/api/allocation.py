from horizon.utils import memoized

from nectar_dashboard.api import usage
from nectar_dashboard.rcallocation import models


@memoized.memoized
def get_current_allocation(request):
    allocations = models.AllocationRequest.objects \
        .filter(project_id=request.user.project_id) \
        .filter(status=models.AllocationRequest.APPROVED)

    no_parents = allocations.filter(parent_request__isnull=True)
    if no_parents:
        return no_parents[0]

    # If the latest approved has a parent then means under
    # renewal so get the last approved allocation.
    if allocations:
        return allocations[0]


@memoized.memoized
def get_quota(request, resource_code):
    allocation = get_current_allocation(request)
    if allocation is None:
        return None

    resource = models.Resource.objects.get_by_codename(resource_code)
    try:
        quota = models.Quota.objects.get(group__allocation=allocation,
                                         resource=resource)
    except models.Quota.DoesNotExist:
        quota = None

    if quota:
        return quota.quota


@memoized.memoized
def get_su_budget(request):
    allocation = get_current_allocation(request)
    if allocation is None:
        return None

    if allocation.bundle:
        return allocation.bundle.su_per_year / 12 \
            * allocation.estimated_project_duration
    else:
        return get_quota(request, 'rating.budget')


@memoized.memoized
def get_usage(request):
    allocation = get_current_allocation(request)
    if allocation is None:
        return None

    begin = allocation.start_date.strftime('%Y-%m-%d')
    end = allocation.end_date.strftime('%Y-%m-%d')
    usage_data = usage.get_summary(request, begin=begin, end=end)

    return usage_data
