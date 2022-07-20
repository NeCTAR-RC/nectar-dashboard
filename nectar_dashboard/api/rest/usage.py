from django.views import generic
from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils

from nectar_dashboard.api import usage


@urls.register
class Summary(generic.View):
    """Cloudkitty summary

    """
    url_regex = r'nectar/usage/summary/$'

    @rest_utils.ajax()
    def get(self, request):
        """List summary

        The listing result is an object with property "items".
        """
        detailed = request.GET.get('detailed', False)
        resource_type = request.GET.get('type', None)
        filters = {}

        if resource_type:
            filters['type'] = resource_type

        return usage.get_summary(request, filters=filters,
                                 detailed=detailed)


@urls.register
class SummaryByType(generic.View):
    """DEPRECATED: Cloudkitty summary for type by type

    Use Summary /api/nectar/usage/summary/?type=instance instead

    """
    url_regex = r'nectar/usage/summary/(?P<resource_type>[^/]+)/$'

    @rest_utils.ajax()
    def get(self, request, resource_type):
        """List summary with resource_type filter
        """
        detailed = request.GET.get('detailed', False)
        filters = {'type': resource_type}
        return usage.get_summary(request, filters=filters, detailed=detailed)


@urls.register
class MostUsedResources(generic.View):
    """API for load balancers.

    """
    url_regex = r'nectar/usage/most-used/(?P<resource_type>[^/]+)/$'

    @rest_utils.ajax()
    def get(self, request, resource_type):
        """List load balancers for current project.

        The listing result is an object with property "items".
        """
        return usage.most_used_resources(request, resource_type)


@urls.register
class InstanceData(generic.View):
    """API for load balancers.

    """
    url_regex = r'nectar/usage/instance-data/$'

    @rest_utils.ajax()
    def get(self, request):
        """List load balancers for current project.

        The listing result is an object with property "items".
        """
        return usage.instance_data(request)
