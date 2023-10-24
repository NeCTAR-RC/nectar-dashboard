from django.utils.translation import gettext_lazy as _

import horizon
from nectar_dashboard.rcallocation import dashboard


class ApprovedRequests(horizon.Panel):
    name = _("Approved Requests")
    slug = 'approved_requests'
    index_url_name = 'approved_requests'
    permissions = ('openstack.roles.allocationadmin',)


dashboard.AllocationsDashboard.register(ApprovedRequests)
