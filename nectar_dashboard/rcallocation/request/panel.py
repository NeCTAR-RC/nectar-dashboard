from django.utils.translation import gettext_lazy as _

import horizon
from nectar_dashboard.rcallocation import dashboard


class Request(horizon.Panel):
    name = _("New Request")
    slug = 'request'
    index_url_name = "request"


dashboard.AllocationsDashboard.register(Request)
