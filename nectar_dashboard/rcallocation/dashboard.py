from django.utils.translation import ugettext_lazy as _

import horizon
from openstack_dashboard.dashboards.project import dashboard


class AllocationsPanels(horizon.PanelGroup):
    slug = "allocation"
    name = _("Allocations")
    panels = ('request', 'requests', 'approved_requests', 'user_requests')

dashboard.Project.panels = dashboard.Project.panels + (AllocationsPanels,)

import allocation.panel
import allocation_approved.panel
import request.panel
import user_allocations.panel
