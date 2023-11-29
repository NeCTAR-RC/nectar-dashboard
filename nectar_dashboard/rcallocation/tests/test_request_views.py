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

from django.urls import reverse

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import common


@mock.patch('nectar_dashboard.rcallocation.notifier.FreshdeskNotifier',
            new=base.FAKE_FD_NOTIFIER_CLASS)
class RequestTestCase(base.BaseTestCase):

    def test_request_allocation(self):
        base.FAKE_FD_NOTIFIER.send_email.reset_mock()

        response = self.client.get(
            reverse('horizon:allocation:request:request'))
        self.assertStatusCode(response, 200)

        expected_model, form = common.request_allocation(user=self.user)

        # Tells the server to skip the sanity checks.  (The request
        # has fuzz'd quota values which tyically won't pass muster.)
        form['ignore_warnings'] = True
        response = self.client.post(
            reverse('horizon:allocation:request:request'),
            form)

        self._assert_success(response)
        model = models.AllocationRequest.objects.get(
            project_description=form['project_description'],
            parent_request_id=None)
        self.assert_allocation(model, **expected_model)
        self.assertTrue(model.managed)
        self.assertTrue(model.notifications)
        base.FAKE_FD_NOTIFIER.send_email.assert_called_once()
        call_kwargs = base.FAKE_FD_NOTIFIER.send_email.mock_calls[0].kwargs
        self.assertEqual("test_user", call_kwargs['email'])
        self.assertEqual(
            f"Allocation request [{form['project_description']}]",
            call_kwargs['subject'])
        # Not checking the expansion of the template body.

    def _assert_success(self, response):
        """Check to make sure we were redirected back to the index of
        our requests.
        """
        self.assertStatusCode(response, 302)
        self.assertTrue(response.get('location').endswith(
            reverse('horizon:allocation:user_requests:index')),
            msg="incorrect redirect location")

    def _test_allocation(self, errors={}, override_form=True, **kwargs):
        """The 'override_form' argument deals with the problem that the
        'common.request_allocation' method has limited ability to handle
        keyword args.
        """
        response = self.client.get(
            reverse('horizon:allocation:request:request'))
        expected_model, form = (
            common.request_allocation(user=self.user) if override_form
            else common.request_allocation(user=self.user, **kwargs))

        if override_form:
            for field, value in kwargs.items():
                form[field] = value

        # Tells the server to skip the sanity checks.  (The request
        # typically has fuzz'd quota values which won't pass muster.)
        form['ignore_warnings'] = True

        response = self.client.post(
            reverse('horizon:allocation:request:request'),
            form)

        if errors:
            # No redirect invalid fields
            self.assertStatusCode(response, 200)
            for e_form, e_errors in errors.items():
                self.assertEqual(response.context[e_form].errors, e_errors)

            return

        self._assert_success(response)

        # Finally check that the expected changes have been made to
        # the model.
        if override_form:
            for field, value in kwargs.items():
                expected_model[field] = value

        model = models.AllocationRequest.objects.get(
            project_description=form['project_description'],
            parent_request_id=None)
        self.assert_allocation(model, **expected_model)

    def test_blank_project_name(self):
        self._test_allocation(
            project_name='',
            errors={'form': {'project_name': [u'This field is required.']}}
        )

    def test_blank_project_description(self):
        self._test_allocation(
            project_description='',
            errors={'form': {'project_description':
                             [u'This field is required.']}}
        )

    def test_blank_geographic_requirements(self):
        self._test_allocation(
            geographic_requirements='',
        )

    def test_blank_use_case(self):
        self._test_allocation(
            use_case='',
            errors={'form': {'use_case': [u'This field is required.']}}
        )

    def test_inconsistent_supported_orgs(self):
        self._test_allocation(
            override_form=False,
            supported_organisations=[
                models.Organisation.objects.get(short_name='Monash'),
                models.Organisation.objects.get(short_name='all')],
            errors={'form': {'supported_organisations': [
                "'All Organisations' should not be used "
                "with any other organisation"]}}
        )

    def test_supported_org_unknown(self):
        self._test_allocation(
            override_form=False,
            supported_organisations=[
                models.Organisation.objects.get(short_name='unknown')],
            errors={'form': {'supported_organisations': [
                "'Unspecified Organisation' should not be used "
                "in this context"]}}
        )

    def test_all_ci_all_organisations(self):
        self._test_allocation(
            override_form=False,
            investigators=[{
                'id': '',
                'title': 'Prof.',
                'given_name': 'Bradley',
                'surname': 'Awl',
                'email': 'brad@somewhere.edu.au',
                'primary_organisation':
                    models.Organisation.objects.get(short_name='all'),
                'additional_researchers': 'None'
            }],
            errors={'investigator_formset': [{
                'primary_organisation': [
                    f"'{models.ORG_ALL_FULL_NAME}' is not meaningful "
                    "in this context"]}]}
        )

    def test_request_quotas_ok(self):
        response = self.client.get(
            reverse('horizon:allocation:request:request'))
        self.assertStatusCode(response, 200)
        quota_specs = [
            common.quota_spec('compute', 'instances', requested_quota=1),
            common.quota_spec('compute', 'cores', requested_quota=2),
            common.quota_spec('rating', 'budget', requested_quota=1000),
        ]
        expected_model, form = common.request_allocation(
            user=self.user, quota_specs=quota_specs)

        response = self.client.post(
            reverse('horizon:allocation:request:request'),
            form)

        self._assert_success(response)
        model = (models.AllocationRequest.objects
                 .get(project_description=form['project_description'],
                      parent_request_id=None))
        self.assert_allocation(model, **expected_model)

    def test_request_quotas_warn(self):
        response = self.client.get(
            reverse('horizon:allocation:request:request'))
        self.assertStatusCode(response, 200)
        quota_specs = [
            common.quota_spec('rating', 'budget', requested_quota=0),
        ]
        expected_model, form = common.request_allocation(
            user=self.user, quota_specs=quota_specs)

        response = self.client.post(
            reverse('horizon:allocation:request:request'),
            form)

        # If there are warnings we will get a 200
        self.assertStatusCode(response, 200)

        # Repeat request ignoring warnings
        form['ignore_warnings'] = True
        response = self.client.post(
            reverse('horizon:allocation:request:request'),
            form)

        self._assert_success(response)
        model = (models.AllocationRequest.objects
                 .get(project_description=form['project_description'],
                      parent_request_id=None))
        self.assert_allocation(model, **expected_model)
