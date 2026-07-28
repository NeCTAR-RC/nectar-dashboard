from datetime import datetime
from datetime import timezone as dt_timezone
from types import SimpleNamespace
from unittest import mock

from nectarclient_lib import exceptions as nectar_exceptions
from openstack_dashboard.test import helpers as test

from nectar_dashboard.api import langstroth as langstroth_api
from nectar_dashboard.api.rest import langstroth


def _announcement(**overrides):
    defaults = {
        'id': 1,
        'title': 't',
        'severity': 2,
        'scheduled': False,
        'scheduled_display': 'unscheduled',
        'status_display': 'In progress',
        'start': datetime(2026, 7, 1, 10, 0, tzinfo=dt_timezone.utc),
        'end': None,
        'planned_end': None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class OutagesRestTestCase(test.RestAPITestCase):
    """The /api/nectar/outages/ proxy merges outages from the legacy
    endpoint with notices and news from v1/announcements.
    """

    def _mock_client(self):
        client = mock.Mock()
        self.mock_langstrothclient.return_value = client
        return client

    @test.create_mocks({langstroth_api: ['langstrothclient']})
    def test_get_merges_categories(self):
        client = self._mock_client()
        # Legacy endpoint rows carry no category attribute.
        outage = _announcement(id=1)
        client.outages.list.side_effect = [[outage], [], []]
        notice = _announcement(id=2, category='notice', severity=3)
        news = _announcement(
            id=3, category='news', severity=None, status_display='Published'
        )
        client.announcements.list.side_effect = [[notice], [news]]

        request = self.mock_rest_request(**{'GET': {}})
        response = langstroth.Outages().get(request)

        self.assertStatusCode(response, 200)
        items = response.json['items']
        self.assertEqual(
            {1: 'outage', 2: 'notice', 3: 'news'},
            {item['id']: item['category'] for item in items},
        )
        news_item = [i for i in items if i['id'] == 3][0]
        self.assertIsNone(news_item['severity'])
        self.assertEqual('Published', news_item['status_display'])

        self.assertEqual(3, client.outages.list.call_count)
        announcement_calls = client.announcements.list.call_args_list
        self.assertEqual(
            mock.call(category='notice', activity='active'),
            announcement_calls[0],
        )
        self.assertEqual('news', announcement_calls[1].kwargs['category'])
        self.assertFalse(announcement_calls[1].kwargs['cancelled'])
        self.assertIn('start__gte', announcement_calls[1].kwargs)

    @test.create_mocks({langstroth_api: ['langstrothclient']})
    def test_get_degrades_without_announcements_endpoint(self):
        # Older langstroth deployments have no v1/announcements; the
        # panel must still serve outages.
        client = self._mock_client()
        client.outages.list.side_effect = [[_announcement(id=1)], [], []]
        client.announcements.list.side_effect = nectar_exceptions.NotFound(404)

        request = self.mock_rest_request(**{'GET': {}})
        response = langstroth.Outages().get(request)

        self.assertStatusCode(response, 200)
        items = response.json['items']
        self.assertEqual([1], [item['id'] for item in items])
        self.assertEqual(['outage'], [item['category'] for item in items])

    @test.create_mocks({langstroth_api: ['langstrothclient']})
    def test_get_dedupes_by_id(self):
        client = self._mock_client()
        outage = _announcement(id=1)
        client.outages.list.side_effect = [[outage], [outage], []]
        client.announcements.list.side_effect = [[], []]

        request = self.mock_rest_request(**{'GET': {}})
        response = langstroth.Outages().get(request)

        self.assertEqual(1, len(response.json['items']))
