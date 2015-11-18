from django.utils.translation import ugettext_lazy as _
from django.conf import settings

import horizon
from openstack_dashboard.dashboards.project import dashboard


class UserRequests(horizon.Panel):
    name = _("My Requests")
    slug = 'user_requests'
    #index_url_name = "user_allocation_requests"
    #permissions = ('openstack.roles.allocationadmin',)

dashboard.Project.register(UserRequests)
