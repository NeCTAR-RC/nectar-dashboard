from django.utils.translation import ugettext_lazy as _

import horizon
from openstack_dashboard.dashboards.project import dashboard


class Request(horizon.Panel):
    name = _("New Request")
    slug = 'request'
    index_url_name = "request"


dashboard.Project.register(Request)
