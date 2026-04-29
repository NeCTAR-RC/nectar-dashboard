from datetime import timedelta

from django.utils import timezone
from django.views import generic
from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils

from nectar_dashboard.api import langstroth


def _serialize_outage(outage):
    return {
        'id': outage.id,
        'title': outage.title,
        'severity': outage.severity,
        'scheduled': outage.scheduled,
        'scheduled_display': outage.scheduled_display,
        'status_display': outage.status_display,
        'scheduled_start': (
            outage.scheduled_start.isoformat()
            if outage.scheduled_start
            else None
        ),
        'scheduled_end': (
            outage.scheduled_end.isoformat() if outage.scheduled_end else None
        ),
        'start': outage.start.isoformat() if outage.start else None,
        'end': outage.end.isoformat() if outage.end else None,
    }


@urls.register
class Outages(generic.View):
    """API for langstroth outages."""

    url_regex = r'nectar/outages/$'

    @rest_utils.ajax()
    def get(self, request):
        """List current and upcoming outages.

        Returns outages that are currently in progress or scheduled within
        the next 14 days, plus any unresolved active outages from the past
        day.
        """
        client = langstroth.langstrothclient(request)
        all_outages = client.outages.list()
        start = timezone.now() - timedelta(days=1)
        end = timezone.now() + timedelta(days=14)
        outages = []
        for o in all_outages:
            if (
                o.scheduled
                and o.scheduled_end > start
                and o.scheduled_start < end
            ) or (o.start and (not o.end or o.end >= start)):
                outages.append(_serialize_outage(o))
        return {'items': outages}
