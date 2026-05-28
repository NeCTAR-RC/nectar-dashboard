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
        'start': outage.start.isoformat(),
        'end': outage.end.isoformat() if outage.end else None,
        'planned_end': (
            outage.planned_end.isoformat() if outage.planned_end else None
        ),
    }


@urls.register
class Outages(generic.View):
    """API for langstroth outages."""

    url_regex = r'nectar/outages/$'

    @rest_utils.ajax()
    def get(self, request):
        """List current and upcoming outages.

        Returns outages that are currently in progress, scheduled to start
        within the next 14 days, or resolved within the past day.

        The langstroth API can't express the "ongoing OR recently-ended"
        set in a single filtered query (there is no ``end__isnull``
        lookup), so we issue three disjoint server-side queries rather than
        fetching every outage and filtering in Python.
        """
        client = langstroth.langstrothclient(request)
        now = timezone.now()
        window_start = (now - timedelta(days=1)).isoformat()
        window_end = (now + timedelta(days=14)).isoformat()

        # In progress now (started, not yet ended, not cancelled).
        active = client.outages.list(activity='active')
        # Scheduled to start within the next 14 days.
        upcoming = client.outages.list(
            activity='upcoming', start__lte=window_end
        )
        # Ended within the past day.
        recent = client.outages.list(cancelled=False, end__gte=window_start)

        # The three queries are disjoint by construction, but dedupe by id
        # to be safe against any overlap in edge-case data.
        outages = {}
        for o in [*active, *upcoming, *recent]:
            outages.setdefault(o.id, o)
        return {'items': [_serialize_outage(o) for o in outages.values()]}
