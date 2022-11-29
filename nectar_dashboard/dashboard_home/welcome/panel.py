from django.utils.translation import ugettext_lazy as _
import horizon

from nectar_dashboard.dashboard_home import dashboard


class Welcome(horizon.Panel):
    name = _('Welcome')
    slug = 'welcome'
    index_url_name = 'welcome'


dashboard.HomeDashboard.register(Welcome)
