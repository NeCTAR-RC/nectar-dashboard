from django.utils.translation import ugettext_lazy as _

import horizon
from nectar_dashboard.rcallocation import dashboard


class CramsRequests(horizon.Panel):
    name = _("Request via CRAMS")
    slug = 'crams_requests'
    index_url_name = "crams_requests"


dashboard.AllocationsDashboard.register(CramsRequests)
