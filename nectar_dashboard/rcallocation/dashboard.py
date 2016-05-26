from django.utils.translation import ugettext_lazy as _

import horizon


class AllocationsDashboard(horizon.Dashboard):
    name = _("Allocations")
    slug = "allocation"
    panels = ('request', 'requests', 'approved_requests', 'user_requests',
              'crams_requests',)
    default_panel = 'request'


horizon.register(AllocationsDashboard)
