from django.utils.translation import ugettext_lazy as _

import horizon
from nectar_dashboard.user_info import dashboard


class UserLookupPanel(horizon.Panel):
    name = _("User Info Lookup")
    slug = 'lookup'
    index_url_name = 'lookup'


dashboard.UserInfoDashboard.register(UserLookupPanel)
