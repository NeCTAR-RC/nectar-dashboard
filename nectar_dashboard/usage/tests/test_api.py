from unittest import mock

from freezegun import freeze_time
from openstack_dashboard.test import helpers

from nectar_dashboard.api import usage


@freeze_time("2022-03-16")
class ApiTest(helpers.APIMockTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.fake_results = [
            {'id': 'instance-1', 'rate': 1.322},
            {'id': 'instance-2', 'rate': 3.456},
            {'id': 'instance-3', 'rate': 4.5},
            {'id': 'instance-4', 'rate': 1.7325},
            {'id': 'instance-5', 'rate': 2},
            {'id': 'instance-6', 'rate': 5.8252},
            {'id': 'instance-7', 'rate': 3.1245},
        ]

    def test_get_begin_end(self):
        begin, end = usage.get_begin_end(self.request)
        self.assertEqual('2021-12-16', begin)
        self.assertEqual('2022-03-16', end)

    def test_get_begin_end_request_params(self):
        self.request.GET['begin'] = '2021-02-01'
        self.request.GET['end'] = '2021-02-23'

        begin, end = usage.get_begin_end(self.request)

        self.assertEqual('2021-02-01', begin)
        self.assertEqual('2021-02-23', end)

    @mock.patch('cloudkittydashboard.api.cloudkitty.cloudkittyclient')
    def test_get_summary(self, mock_cloudkitty):
        summary = usage.get_summary(self.request, 'instance')
        mock_cloudkitty.assert_called_once_with(self.request, version='2')
        client = mock_cloudkitty.return_value

        client.summary.get_summary.assert_called_once_with(
            begin='2021-12-16', end='2022-03-16',
            filters={'type': 'instance'},
            response_format='object', limit=1000)

        self.assertEqual(
            client.summary.get_summary.return_value.get('results'),
            summary)

    @mock.patch('cloudkittydashboard.api.cloudkitty.cloudkittyclient')
    def test_get_summary_with_dates(self, mock_cloudkitty):
        summary = usage.get_summary(self.request, 'instance',
                                    begin='2000-01-01', end='2000-02-01')
        mock_cloudkitty.assert_called_once_with(self.request, version='2')
        client = mock_cloudkitty.return_value

        client.summary.get_summary.assert_called_once_with(
            begin='2000-01-01', end='2000-02-01',
            filters={'type': 'instance'},
            response_format='object', limit=1000)

        self.assertEqual(
            client.summary.get_summary.return_value.get('results'),
            summary)

    @mock.patch('cloudkittydashboard.api.cloudkitty.cloudkittyclient')
    def test_get_summary_detailed(self, mock_cloudkitty):
        client = mock_cloudkitty.return_value
        client.summary.get_summary.return_value = \
            {'results': self.fake_results}

        summary = usage.get_summary(self.request, 'instance', detailed=True)

        mock_cloudkitty.assert_called_once_with(self.request, version='2')

        client.summary.get_summary.assert_called_once_with(
            begin='2021-12-16', end='2022-03-16',
            filters={'type': 'instance'},
            response_format='object', limit=1000)

        expected = {'sum': 21.96, 'data': self.fake_results}
        self.assertEqual(expected, summary)

    @mock.patch('cloudkittydashboard.api.cloudkitty.cloudkittyclient')
    def test_most_used_resources(self, mock_cloudkitty):

        with mock.patch.object(usage, 'instance_data') as mock_instance_data:
            mock_instance_data.return_value = self.fake_results
            data = usage.most_used_resources(self.request, 'instance')

            expected = {'count': 7, 'data': [
                {'instance-6': 5.8252},
                {'instance-3': 4.5},
                {'instance-2': 3.456},
                {'instance-7': 3.1245},
                {'instance-5': 2},
                {'other': 3.05},
            ]}
            self.assertEqual(expected, data)

    @mock.patch('nectar_dashboard.api.gnocchi.gnocchiclient')
    @mock.patch('cloudkittydashboard.api.cloudkitty.cloudkittyclient')
    def test_instance_data(self, mock_cloudkitty, mock_gnocchi):
        self.maxDiff = None
        client = mock_cloudkitty.return_value
        g_client = mock_gnocchi.return_value

        g_client.resource.search.return_value = [
            {'id': 'instance-1', 'availability_zone': 'foo',
             'flavor_name': 'm2.small', 'user_id': 'user-123',
             'started_at': '2021-01-01', 'ended_at': None},
            {'id': 'instance-2', 'availability_zone': 'mel',
             'flavor_name': 'm1.medium', 'display_name': 'name123',
             'started_at': '2021-03-01', 'ended_at': '2031-03-05'},
        ]

        client.summary.get_summary.return_value = {
            'results': self.fake_results}

        data = usage.instance_data(self.request)

        g_client.resource.search.assert_called_once_with(
            resource_type='instance',
            query=('ended_at=null or ended_at >= "2021-12-15"'),
        )
        expected_data = [
            {'id': 'instance-1', 'rate': 1.32,
             'availability_zone': 'foo',
             'flavor_name': 'm2.small',
             'display_name': None,
             'started_at': '2021-01-01',
             'ended_at': None},
            {'id': 'instance-2', 'rate': 3.46,
             'availability_zone': 'mel',
             'flavor_name': 'm1.medium',
             'display_name': 'name123',
             'started_at': '2021-03-01',
             'ended_at': '2031-03-05'},
            {'id': 'instance-3', 'rate': 4.5},
            {'id': 'instance-4', 'rate': 1.73},
            {'id': 'instance-5', 'rate': 2},
            {'id': 'instance-6', 'rate': 5.83},
            {'id': 'instance-7', 'rate': 3.12}
            ]

        self.assertEqual(expected_data, data)
