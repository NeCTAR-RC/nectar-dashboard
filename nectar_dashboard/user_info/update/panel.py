from django.utils.translation import ugettext_lazy as _

import horizon
from nectar_dashboard.user_info import dashboard


class UserUpdatePanel(horizon.Panel):
    name = _("User Info Update")
    slug = 'update'
    index_url_name = 'edit-self'


dashboard.UserInfoDashboard.register(UserUpdatePanel)
