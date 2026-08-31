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

from rest_framework import exceptions
from rest_framework import status

from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import utils
from nectar_dashboard import rest_auth


def valid_token(*args, **kwargs):
    return True


def expired_token(*args, **kwargs):
    return False


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
    def _request(self, token='a-token'):
        request = mock.Mock()
        request.META = {'HTTP_X_AUTH_TOKEN': token} if token else {}
        request.environ = {'REMOTE_ADDR': '127.0.0.1'}
        return request

    def test_no_token_is_not_authenticated(self):
        auth = rest_auth.KeystoneAuthentication()
        self.assertIsNone(auth.authenticate(self._request(token=None)))

    def test_token_is_authenticated_without_logging_in(self):
        user = utils.get_user()
        with (
            mock.patch.object(
                rest_auth.auth_utils, 'validate_token', create=True
            ),
            mock.patch.object(
                rest_auth.auth, 'authenticate', return_value=user
            ),
            mock.patch.object(rest_auth.auth, 'login') as login,
        ):
            result = rest_auth.KeystoneAuthentication().authenticate(
                self._request()
            )

        self.assertEqual((user, None), result)
        # Logging in would hand the API client a Django session cookie that
        # then takes over authentication from the token it sends.
        login.assert_not_called()

    def test_unusable_token_is_rejected(self):
        with (
            mock.patch.object(
                rest_auth.auth_utils, 'validate_token', create=True
            ),
            mock.patch.object(
                rest_auth.auth, 'authenticate', return_value=None
            ),
        ):
            self.assertRaises(
                exceptions.AuthenticationFailed,
                rest_auth.KeystoneAuthentication().authenticate,
                self._request(),
            )

    def test_request_with_a_token_sets_no_session_cookie(self):
        user = utils.get_user()
        with (
            mock.patch.object(
                rest_auth.auth_utils, 'validate_token', create=True
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
