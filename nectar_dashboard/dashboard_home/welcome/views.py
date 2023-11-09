from datetime import timedelta
import logging

from django import http
from django.utils import timezone
from django.views.decorators import cache
from horizon import views as horizon_views
import requests

from nectar_dashboard.api import langstroth
from nectar_dashboard.api import manuka

LOG = logging.getLogger(__name__)


class HomeView(horizon_views.HorizonTemplateView):

    template_name = 'dashboard_home/home.html'
    page_title = "Home"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            keystone_id = self.request.user.keystone_user_id
            client = manuka.manukaclient(self.request)
            self.manuka_user = client.users.get(keystone_id)
            context['first_name'] = self.manuka_user.first_name
            context['surname'] = self.manuka_user.surname
            context['displayname'] = self.manuka_user.displayname
        except Exception as e:
            LOG.error("Manuka account lookup failed", exc_info=e)
            context['first_name'] = ""
            context['surname'] = ""
            context['displayname'] = ""

        try:
            client = langstroth.langstrothclient(self.request)
            all_outages = client.outages.list()
            # TODO(SC): make the start and end deltas Dashboardsettings, and
            # do the filtering in the Langstroth Outages API.
            start = timezone.now() - timedelta(days=1)
            end = timezone.now() + timedelta(days=14)
            outages = []
            for o in all_outages:
                if ((o.scheduled
                     and o.scheduled_end > start
                     and o.scheduled_start < end)
                    or (o.start and (
                        not o.end or o.end >= start))):
                    outages.append(o)
            context['outages'] = outages
        except Exception as e:
            LOG.error("Langstroth outage lookup failed", exc_info=e)
            context['outages'] = []

        LOG.error("Home page context is %s", context)
        return context


@cache.cache_page(3600)
def get_ardc_news(request):

    url = 'https://ardc.edu.au/feed/latest-articles/'
    req = requests.get(url=url)
    return http.HttpResponse(req.text,
                             content_type=req.headers['Content-Type'])
