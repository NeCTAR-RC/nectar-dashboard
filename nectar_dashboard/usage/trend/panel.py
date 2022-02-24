from django.utils.translation import ugettext_lazy as _

import horizon
from openstack_dashboard.dashboards.project import dashboard


class Trend(horizon.Panel):
    name = _('Usage Trend')
    slug = 'usage-trend'


dashboard.Project.register(Trend)
