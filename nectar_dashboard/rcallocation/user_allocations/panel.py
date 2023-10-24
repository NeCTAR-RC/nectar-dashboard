from django.utils.translation import gettext_lazy as _
import horizon

from nectar_dashboard.rcallocation import dashboard


class UserRequests(horizon.Panel):
    name = _("My Requests")
    slug = 'user_requests'


dashboard.AllocationsDashboard.register(UserRequests)
