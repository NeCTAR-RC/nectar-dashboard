from django.utils.translation import gettext_lazy as _

import horizon

# DO NOT REMOVE
# This needs for register url of REST API.
# Dashboard plugins load REST API from here.
from nectar_dashboard.api import rest  # noqa


class AllocationsDashboard(horizon.Dashboard):
    name = _("Allocations")
    slug = "allocation"
    panels = ('request', 'requests', 'approved_requests', 'user_requests')
    default_panel = 'request'


horizon.register(AllocationsDashboard)
