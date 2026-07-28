from datetime import timedelta

from django.utils import timezone
from django.views import generic
from nectarclient_lib import exceptions as nectar_exceptions
from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils

from nectar_dashboard.api import langstroth


def _serialize_announcement(announcement):
    return {
        'id': announcement.id,
        'title': announcement.title,
        # The legacy v1/outages endpoint has no category field: every
        # row it returns is an outage.
        'category': getattr(announcement, 'category', 'outage'),
        'severity': announcement.severity,
        'scheduled': announcement.scheduled,
        'scheduled_display': announcement.scheduled_display,
        'status_display': announcement.status_display,
        'start': announcement.start.isoformat(),
        'end': announcement.end.isoformat() if announcement.end else None,
        'planned_end': (
            announcement.planned_end.isoformat()
            if announcement.planned_end
            else None
        ),
    }


@urls.register
class Outages(generic.View):
    """API for langstroth announcements (outages, notices, news)."""

    url_regex = r'nectar/outages/$'

    @rest_utils.ajax()
    def get(self, request):
        """List announcements of current interest.

        Returns outages that are currently in progress, scheduled to start
        within the next 14 days, or resolved within the past day; plus
        active hazard/security notices and news published within the past
        14 days.

        The langstroth API can't express the "ongoing OR recently-ended"
        set in a single filtered query (there is no ``end__isnull``
        lookup), so we issue three disjoint server-side queries rather than
        fetching every outage and filtering in Python.
        """
        client = langstroth.langstrothclient(request)
        now = timezone.now()
        window_start = (now - timedelta(days=1)).isoformat()
        window_end = (now + timedelta(days=14)).isoformat()
        news_window_start = (now - timedelta(days=14)).isoformat()

        # In progress now (started, not yet ended, not cancelled).
        active = client.outages.list(activity='active')
        # Scheduled to start within the next 14 days.
        upcoming = client.outages.list(
            activity='upcoming', start__lte=window_end
        )
        # Ended within the past day.
        recent = client.outages.list(cancelled=False, end__gte=window_start)

        # Hazard/security notices and news ride the newer
        # v1/announcements endpoint. Older langstroth deployments don't
        # have it (ClientException), and langstrothclient < 1.1.0 has
        # no announcements manager (AttributeError); degrade to
        # outages-only rather than breaking the whole panel. (Embargoed
        # future-dated news is hidden server side; retracted items are
        # excluded via cancelled=False.)
        notices = news = []
        try:
            notices = client.announcements.list(
                category='notice', activity='active'
            )
            news = client.announcements.list(
                category='news',
                cancelled=False,
                start__gte=news_window_start,
            )
        except (AttributeError, nectar_exceptions.ClientException):
            pass

        # Outages, notices and news share one ID space in langstroth,
        # and the queries are disjoint by construction; dedupe by id to
        # be safe against any overlap in edge-case data.
        announcements = {}
        for a in [*active, *upcoming, *recent, *notices, *news]:
            announcements.setdefault(a.id, a)
        return {
            'items': [
                _serialize_announcement(a) for a in announcements.values()
            ]
        }
