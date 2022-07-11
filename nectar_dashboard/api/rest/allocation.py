from django.views import generic
from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils

from nectar_dashboard.api import allocation


@urls.register
class Quota(generic.View):
    """API for Quotas.

    """
    url_regex = r'nectar/allocation/quota/(?P<resource_code>[^/]+)/$'

    @rest_utils.ajax()
    def get(self, request, resource_code):
        """Get quota for a given resource

        """
        return allocation.get_quota(request, resource_code)


@urls.register
class Usage(generic.View):
    """API for usage.

    """
    url_regex = r'nectar/allocation/usage/$'

    @rest_utils.ajax()
    def get(self, request):
        """Get su usage for an allocation

        """
        return allocation.get_usage(request)
