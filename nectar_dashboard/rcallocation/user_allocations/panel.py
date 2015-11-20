from django.utils.translation import ugettext_lazy as _

import horizon
from nectar_dashboard.rcallocation import dashboard


class UserRequests(horizon.Panel):
    name = _("My Requests")
    slug = 'user_requests'
    #index_url_name = "user_allocation_requests"
    #permissions = ('openstack.roles.allocationadmin',)

dashboard.AllocationsDashboard.register(UserRequests)
