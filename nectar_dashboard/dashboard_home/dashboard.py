from django.utils.translation import ugettext_lazy as _

import horizon


class HomeDashboard(horizon.Dashboard):
    name = _('Home')
    slug = 'dashboard_home'
    panels = ('welcome',)
    default_panel = 'welcome'


horizon.register(HomeDashboard)
