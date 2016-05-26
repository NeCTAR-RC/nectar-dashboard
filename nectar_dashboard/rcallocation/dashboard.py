from django.utils.translation import ugettext_lazy as _

import horizon


class AllocationsDashboard(horizon.Dashboard):
    name = _("Allocations")
    slug = "allocation"
    # panels = ('request', 'requests', 'approved_requests', 'user_requests',)
    panels = ('crams_requests',)
    default_panel = 'crams_requests'


horizon.register(AllocationsDashboard)
