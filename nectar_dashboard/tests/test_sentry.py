import os
from unittest import mock

from django.test import SimpleTestCase

from nectar_dashboard import sentry


DSN = 'https://key@glitchtip.example.com/1'
RELEASE = 'nectar-dashboard@1.0.0'


@mock.patch('nectar_dashboard.sentry._release', return_value=RELEASE)
@mock.patch('nectar_dashboard.sentry.sentry_sdk')
class SentrySetupTests(SimpleTestCase):
    def test_setup_no_dsn(self, mock_sdk, mock_release):
        with mock.patch.dict(os.environ):
            os.environ.pop('SENTRY_DSN', None)
            self.assertFalse(sentry.setup())
        mock_sdk.init.assert_not_called()

    def test_setup(self, mock_sdk, mock_release):
        with mock.patch.dict(os.environ):
            os.environ.pop('SENTRY_DSN', None)
            self.assertTrue(sentry.setup(DSN, 'testing'))
        mock_sdk.init.assert_called_once_with(
            dsn=DSN,
            environment='testing',
            release=RELEASE,
            in_app_include=sentry.IN_APP_INCLUDE,
            traces_sample_rate=0.0,
            auto_session_tracking=False,
        )

    def test_setup_no_environment(self, mock_sdk, mock_release):
        self.assertTrue(sentry.setup(DSN))
        mock_sdk.init.assert_called_once_with(
            dsn=DSN,
            environment=None,
            release=RELEASE,
            in_app_include=sentry.IN_APP_INCLUDE,
            traces_sample_rate=0.0,
            auto_session_tracking=False,
        )

    def test_setup_dsn_from_environment(self, mock_sdk, mock_release):
        with mock.patch.dict(os.environ, {'SENTRY_DSN': DSN}):
            self.assertTrue(sentry.setup())
        self.assertEqual(DSN, mock_sdk.init.call_args.kwargs['dsn'])

    def test_setup_traces_sample_rate(self, mock_sdk, mock_release):
        self.assertTrue(sentry.setup(DSN, traces_sample_rate=0.1))
        self.assertEqual(
            0.1, mock_sdk.init.call_args.kwargs['traces_sample_rate']
        )

    def test_setup_init_error(self, mock_sdk, mock_release):
        mock_sdk.init.side_effect = Exception('bad dsn')
        with self.assertLogs('nectar_dashboard.sentry', level='ERROR'):
            self.assertFalse(sentry.setup(DSN))


class ReleaseTests(SimpleTestCase):
    def test_release(self):
        with mock.patch('nectar_dashboard.sentry.version') as mock_version:
            release_string = mock_version.version_info.release_string
            release_string.return_value = '1.2.3'
            self.assertEqual('nectar-dashboard@1.2.3', sentry._release())

    def test_release_unknown(self):
        with mock.patch('nectar_dashboard.sentry.version') as mock_version:
            release_string = mock_version.version_info.release_string
            release_string.side_effect = Exception('no version')
            self.assertIsNone(sentry._release())
