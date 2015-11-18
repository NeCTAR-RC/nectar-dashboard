from django.utils.translation import ugettext_lazy as _

import horizon
from openstack_dashboard.dashboards.project import dashboard


class Requests(horizon.Panel):
    name = _("Requests")
    slug = 'requests'
    index_url_name = "allocation_requests"
    permissions = ('openstack.roles.allocationadmin',)


dashboard.Project.register(Requests)
