from django.views import generic
from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils

from nectar_dashboard.api import allocation as allocation_api
from nectar_dashboard.rcallocation.api import allocations


@urls.register
class CurrentAllocation(generic.View):
    """API for Quotas."""

    url_regex = r'nectar/allocation/current/$'

    @rest_utils.ajax()
    def get(self, request):
        """Get the current allocation for the context"""
        allocation = allocation_api.get_current_allocation(request)
        return allocations.AllocationSerializer(allocation).data


@urls.register
class Quota(generic.View):
    """API for Quotas."""

    url_regex = r'nectar/allocation/quota/(?P<resource_code>[^/]+)/$'

    @rest_utils.ajax()
    def get(self, request, resource_code):
        """Get quota for a given resource"""
        quota = allocation_api.get_quota(request, resource_code)
        if quota is not None:
            return quota
        return -1


@urls.register
class SUBudget(generic.View):
    """API for SU Budget."""

    url_regex = r'nectar/allocation/su-budget/$'

    @rest_utils.ajax()
    def get(self, request):
        """Get SU budget for current allocation"""
        budget = allocation_api.get_su_budget(request)
        if budget is not None:
            return budget
        return -1


@urls.register
class Usage(generic.View):
    """API for usage."""

    url_regex = r'nectar/allocation/usage/$'

    @rest_utils.ajax()
    def get(self, request):
        """Get su usage for an allocation"""
        usage = allocation_api.get_usage(request)
        if usage:
            return usage
        return [{'rate': 0, 'qty': 0}]
