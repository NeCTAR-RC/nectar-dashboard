#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from unittest import mock

from django import test
from django.test import RequestFactory

from openstack_auth import exceptions as oa_exceptions

from rest_framework import exceptions
from rest_framework import status

from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import utils
from nectar_dashboard import rest_auth


def valid_token(*args, **kwargs):
    return True


def expired_token(*args, **kwargs):
    return False


class PathMatchesTest(test.SimpleTestCase):
    def test_exact(self):
        self.assertTrue(
            rest_auth.path_matches(
                '/rest_api/allocations/', '/rest_api/allocations/'
            )
        )

    def test_no_match(self):
        self.assertFalse(
            rest_auth.path_matches('/rest_api/zones/', '/rest_api/sites/')
        )

    def test_prefix_only_does_not_match(self):
        self.assertFalse(
            rest_auth.path_matches(
                '/rest_api/allocations/123/', '/rest_api/allocations/'
            )
        )

    def test_single_wildcard(self):
        self.assertTrue(
            rest_auth.path_matches(
                '/rest_api/allocations/123/approve/',
                '/rest_api/allocations/*/approve/',
            )
        )

    def test_single_wildcard_one_segment_only(self):
        self.assertFalse(
            rest_auth.path_matches(
                '/rest_api/allocations/123/approve/',
                '/rest_api/*/approve/',
            )
        )

    def test_recursive_wildcard(self):
        self.assertTrue(
            rest_auth.path_matches(
                '/rest_api/allocations/123/approve/', '/rest_api/**'
            )
        )

    def test_tag(self):
        self.assertTrue(
            rest_auth.path_matches(
                '/rest_api/allocations/123/',
                '/rest_api/allocations/{allocation_id}/',
            )
        )


class ValidateTokenTest(test.TestCase):
    @mock.patch('openstack_auth.utils.get_keystone_client')
    def test_declares_access_rules_support(self, mock_get_client):
        client = mock_get_client.return_value.Client.return_value
        client.tokens.get_token_data.return_value = {'token': {}}

        with mock.patch.object(rest_auth.access, 'AccessInfoV3') as mock_info:
            result = rest_auth.validate_token('fake-token', '127.0.0.1')

        client.tokens.get_token_data.assert_called_once_with(
            'fake-token',
            access_rules_support=rest_auth.ACCESS_RULES_VERSION,
        )
        self.assertEqual(result, mock_info.return_value)


class CsrfExemptSessionAuthenticationTest(base.AllocationAPITest):
    def _authenticate(self, user):
        request = mock.Mock()
        request._request = mock.Mock(user=user)
        return rest_auth.CsrfExemptSessionAuthentication().authenticate(
            request
        )

    @mock.patch('openstack_auth.utils.is_token_valid', new=valid_token)
    def test_session_is_accepted(self):
        user = utils.get_user()
        self.assertEqual((user, None), self._authenticate(user))

    @mock.patch('openstack_auth.utils.is_token_valid', new=expired_token)
    def test_stale_session_is_ignored(self):
        # An openstack_auth user is still 'active' once its keystone token
        # has expired.  Accepting it would stop the token authenticator ever
        # running, and leave views treating the request as anonymous.
        user = utils.get_user()
        self.assertIsNone(self._authenticate(user))


@mock.patch('openstack_auth.utils.is_token_valid', new=valid_token)
class KeystoneAuthenticationTest(base.AllocationAPITest):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.auth = rest_auth.KeystoneAuthentication()

    def make_auth_ref(self, access_rules=None):
        auth_ref = mock.Mock()
        auth_ref.application_credential_access_rules = access_rules
        auth_ref.auth_token = 'fake-token'
        auth_ref.project_id = 'fake-project'
        return auth_ref

    def authenticate(self, auth_ref, method='get', path='/rest_api/zones/'):
        request = getattr(self.factory, method)(
            path, HTTP_X_AUTH_TOKEN='fake-token'
        )
        with (
            mock.patch.object(
                rest_auth, 'validate_token', return_value=auth_ref
            ),
            mock.patch.object(rest_auth, 'auth') as mock_auth,
        ):
            result = self.auth.authenticate(request)
        return result, mock_auth

    def test_no_token(self):
        request = self.factory.get('/rest_api/zones/')
        self.assertIsNone(self.auth.authenticate(request))

    def test_invalid_token(self):
        request = self.factory.get(
            '/rest_api/zones/', HTTP_X_AUTH_TOKEN='fake-token'
        )
        with mock.patch.object(
            rest_auth,
            'validate_token',
            side_effect=oa_exceptions.KeystoneAuthException('invalid'),
        ):
            self.assertRaises(
                exceptions.AuthenticationFailed,
                self.auth.authenticate,
                request,
            )

    def test_unusable_token_is_rejected(self):
        request = self.factory.get(
            '/rest_api/zones/', HTTP_X_AUTH_TOKEN='fake-token'
        )
        with (
            mock.patch.object(
                rest_auth,
                'validate_token',
                return_value=self.make_auth_ref(),
            ),
            mock.patch.object(
                rest_auth.auth, 'authenticate', return_value=None
            ),
        ):
            self.assertRaises(
                exceptions.AuthenticationFailed,
                self.auth.authenticate,
                request,
            )

    def test_token_without_access_rules(self):
        auth_ref = self.make_auth_ref()
        result, mock_auth = self.authenticate(auth_ref)
        self.assertEqual(result, (mock_auth.authenticate.return_value, None))
        # Logging in would hand the API client a Django session cookie that
        # then takes over authentication from the token it sends.
        mock_auth.login.assert_not_called()

    def test_token_with_matching_access_rule(self):
        auth_ref = self.make_auth_ref(
            access_rules=[
                {
                    'service': 'allocations',
                    'method': 'GET',
                    'path': '/rest_api/zones/',
                }
            ]
        )
        result, mock_auth = self.authenticate(auth_ref)
        self.assertEqual(result, (mock_auth.authenticate.return_value, None))
        # Restricted tokens must not be given a session
        mock_auth.login.assert_not_called()

    def test_token_with_wildcard_access_rule(self):
        auth_ref = self.make_auth_ref(
            access_rules=[
                {
                    'service': 'allocations',
                    'method': 'GET',
                    'path': '/rest_api/**',
                }
            ]
        )
        result, mock_auth = self.authenticate(auth_ref)
        self.assertEqual(result, (mock_auth.authenticate.return_value, None))

    def test_token_with_non_matching_path(self):
        auth_ref = self.make_auth_ref(
            access_rules=[
                {
                    'service': 'allocations',
                    'method': 'GET',
                    'path': '/rest_api/sites/',
                }
            ]
        )
        self.assertRaises(
            exceptions.AuthenticationFailed, self.authenticate, auth_ref
        )

    def test_token_with_non_matching_method(self):
        auth_ref = self.make_auth_ref(
            access_rules=[
                {
                    'service': 'allocations',
                    'method': 'GET',
                    'path': '/rest_api/zones/',
                }
            ]
        )
        self.assertRaises(
            exceptions.AuthenticationFailed,
            self.authenticate,
            auth_ref,
            method='post',
        )

    def test_token_with_non_matching_service(self):
        auth_ref = self.make_auth_ref(
            access_rules=[
                {
                    'service': 'compute',
                    'method': 'GET',
                    'path': '/rest_api/zones/',
                }
            ]
        )
        self.assertRaises(
            exceptions.AuthenticationFailed, self.authenticate, auth_ref
        )

    def test_token_with_empty_access_rules(self):
        auth_ref = self.make_auth_ref(access_rules=[])
        self.assertRaises(
            exceptions.AuthenticationFailed, self.authenticate, auth_ref
        )

    def test_request_with_a_token_sets_no_session_cookie(self):
        user = utils.get_user()
        with (
            mock.patch.object(
                rest_auth,
                'validate_token',
                return_value=self.make_auth_ref(),
            ),
            mock.patch.object(
                rest_auth.auth, 'authenticate', return_value=user
            ),
        ):
            response = self.client.get(
                '/rest_api/allocations/', HTTP_X_AUTH_TOKEN='a-token'
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('sessionid', response.cookies)
