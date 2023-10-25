from datetime import datetime
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

# Outage Status
STARTED = 'S'
INVESTIGATING = 'IN'
IDENTIFIED = 'ID'
PROGRESSING = 'P'
FIXED = 'F'
RESOLVED = 'R'
COMPLETED = 'C'
STATUS_DISPLAY = {
    STARTED: 'Started',
    INVESTIGATING: 'Investigating',
    IDENTIFIED: 'Identified',
    PROGRESSING: 'Progressing',
    FIXED: 'Fixed',
    RESOLVED: 'Resolved',
    COMPLETED: 'Completed'
}

# Outage Severity
MINIMAL = 1
SIGNIFICANT = 2
SEVERE = 3
SEVERITY_DISPLAY = {
    MINIMAL: 'Minimal',
    SIGNIFICANT: 'Significant',
    SEVERE: 'Severe'
}


class OutageWrapper(object):
    # Wrap the Outage object returned by the Langstroth client to make
    # it 'nice' for templating.  The added properties are intended
    # to mirror the Outage properties defined in the Langstroth model.

    def __init__(self, outage):
        self._outage = outage

    def __getattr__(self, k):
        return getattr(self._outage, k)

    def scheduled_start_ts(self):
        return self._convert(self._outage.scheduled_start)

    def scheduled_end_ts(self):
        return self._convert(self._outage.scheduled_end)

    def start_ts(self):
        if self._outage.updates:
            return self._convert(self._outage.updates[0]['time'])
        else:
            return None

    def end_ts(self):
        if (self._outage.updates
            and self._outage.updates[-1]['status'] in {COMPLETED, RESOLVED}):
            return self._convert(self._outage.updates[-1]['time'])
        else:
            return None

    def scheduled_display(self):
        return ("Cancelled" if self._outage.cancelled
                else "Scheduled" if self._outage.scheduled
                else "Unscheduled")

    def status_display(self):
        return (STATUS_DISPLAY[self._outage.updates[-1]['status']]
                if self._outage.updates else "Not Started")

    def severity(self):
        return (self._outage.updates[-1]['severity'] if self._outage.updates
                else self._outage.scheduled_severity)

    def severity_display(self):
        severity = self.severity()
        return SEVERITY_DISPLAY[severity] if severity else "Unknown"

    def _convert(self, v):
        try:
            return datetime.fromisoformat(v) if v else None
        except ValueError:
            LOG.error(f"Unrecognized timestamp ({v})")
            return None


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
            outages = client.outages.list()
            # TODO(SC): make the start and end deltas Dashboardsettings, and
            # do the filtering in the Langstroth Outages API.
            start = timezone.now() - timedelta(days=1)
            end = timezone.now() + timedelta(days=14)
            wrappers = []
            for o in outages:
                w = OutageWrapper(o)
                if ((w.scheduled
                     and w.scheduled_end_ts() > start
                     and w.scheduled_start_ts() < end)
                    or (w.start_ts() and (
                        not w.end_ts() or w.end_ts() >= start))):
                    wrappers.append(w)
            context['outages'] = wrappers
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
