from django.utils.translation import ugettext_lazy as _

import horizon


class AllocationsDashboard(horizon.Dashboard):
    name = _("Allocations")
    slug = "allocation"
    panels = ('crams_requests',)
    default_panel = 'crams_requests'


horizon.register(AllocationsDashboard)
