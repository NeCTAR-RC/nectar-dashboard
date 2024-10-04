from django.utils.translation import gettext_lazy as _

import horizon
from openstack_dashboard.dashboards.project import dashboard

from nectar_dashboard.rcallocation import models


class AllocationUsage(horizon.Panel):
    name = _('Allocation Usage')
    slug = 'allocation-usage'

    def allowed(self, context):
        """Only show panel if allocation has a budget"""

        project_id = context['request'].user.project_id

        allocations = models.AllocationRequest.objects.filter(
            project_id=project_id
        ).filter(status=models.AllocationRequest.APPROVED)

        if allocations:
            allocation = allocations[0]
            if allocation.su_budget and allocation.su_budget > 0:
                return True
        return False


dashboard.Project.register(AllocationUsage)
