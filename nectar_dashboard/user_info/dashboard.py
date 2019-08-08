from django.utils.translation import ugettext_lazy as _

import horizon


class UserInfoDashboard(horizon.Dashboard):
    name = _("User Info")
    slug = "user-info"
    panels = ('lookup', 'update')
    default_panel = 'lookup'


horizon.register(UserInfoDashboard)
