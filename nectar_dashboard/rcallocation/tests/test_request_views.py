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

    def assert_allocation(self, model, quotas=[],
                          institutions=[], publications=[],
                          grants=[], investigators=[],
                          surveys=[], **attributes):

        for field, value in attributes.items():
            if field not in ['quotas', 'institutions', 'publications',
                             'grants', 'investigators', 'usage_types']:
                self.assertEqual(getattr(model, field), value,
                                 "field that didn't match: %s" % field)
        self.assertEqual(list(attributes['usage_types']),
                         list(model.usage_types.all()))
        self.assertEqual(model.contact_email, self.user.name)
        quotas_l = models.Quota.objects.filter(group__allocation=model)
        # (For ... reasons ... there may be zero-valued quotas in the list)
        quotas = [q for q in quotas if q['quota'] > 0
                  or q['requested_quota'] > 0]
        self.assertEqual(quotas_l.count(), len(quotas))
        # (The order of the quotas don't need to match ...)
        for qm in quotas_l:
            matched = [q for q in quotas if q['resource'] == qm.resource.id
                       and q['zone'] == qm.group.zone.name]
            self.assertEqual(len(matched), 1)
            self.assertEqual(qm.group.zone.name, matched[0]['zone'])
            self.assertEqual(qm.requested_quota,
                             matched[0]['requested_quota'])
            self.assertEqual(qm.quota, matched[0]['quota'])

        institutions_l = model.institutions.all()
        for i, institution_model in enumerate(institutions_l):
            self.assertEqual(institution_model.name, institutions[i]['name'])

        publications_l = model.publications.all()
        for i, pub_model in enumerate(publications_l):
            self.assertEqual(pub_model.publication,
                             publications[i]['publication'])

        grants_l = model.grants.all()
        for i, g_model in enumerate(grants_l):
            self.assertEqual(g_model.grant_type, grants[i]['grant_type'])
            self.assertEqual(g_model.funding_body_scheme, grants[i][
                'funding_body_scheme'])
            self.assertEqual(g_model.grant_id, grants[i]['grant_id'])
            self.assertEqual(g_model.first_year_funded,
                             grants[i]['first_year_funded'])
            self.assertEqual(g_model.last_year_funded,
                             grants[i]['last_year_funded'])
            self.assertEqual(g_model.total_funding, grants[i]['total_funding'])

        investigators_l = model.investigators.all()
        for i, inv_m in enumerate(investigators_l):
            self.assertEqual(inv_m.title, investigators[i]['title'])
            self.assertEqual(inv_m.given_name, investigators[i]['given_name'])
            self.assertEqual(inv_m.surname, investigators[i]['surname'])
            self.assertEqual(inv_m.email, investigators[i]['email'])
            self.assertEqual(inv_m.institution,
                             investigators[i]['institution'])
            self.assertEqual(inv_m.additional_researchers, investigators[i][
                'additional_researchers'])

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

        # Check to make sure we were redirected back to the index of
        # our requests.
        self.assertStatusCode(response, 302)
        self.assertTrue(response.get('location').endswith(
            reverse('horizon:allocation:user_requests:index')),
            msg="incorrect redirect location")
        model = (models.AllocationRequest.objects
                 .get(project_description=form['project_description'],
                      parent_request_id=None))
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

    def _test_allocation(self, form_errors={},
                         **kwargs):
        response = self.client.get(
            reverse('horizon:allocation:request:request'))
        expected_model, form = common.request_allocation(user=self.user)
        backup_values = {}

        for field, value in kwargs.items():
            self.assertIn(field, form)
            backup_values[field] = form[field]
            form[field] = value

        # Tells the server to skip the sanity checks.  (The request
        # has fuzz'd quota values which tyically won't pass muster.)
        form['ignore_warnings'] = True

        response = self.client.post(
            reverse('horizon:allocation:request:request'),
            form)

        if form_errors:
            # No redirect invalid fields
            self.assertStatusCode(response, 200)
            self.assertEqual(response.context['form'].errors, form_errors)

            for field, value in backup_values.items():
                form[field] = backup_values[field]
            response = self.client.post(
                reverse('horizon:allocation:request:request'),
                form)
        else:
            for field, value in kwargs.items():
                expected_model[field] = value

        # Check to make sure we were redirected back to the index of
        # our requests.
        self.assertStatusCode(response, 302)
        self.assertTrue(response.get('location').endswith(
            reverse('horizon:allocation:user_requests:index')),
            msg="incorrect redirect location")

        model = (models.AllocationRequest.objects
                 .get(project_description=form['project_description'],
                      parent_request_id=None))
        self.assert_allocation(model, **expected_model)

    def test_blank_project_name(self):
        self._test_allocation(
            project_name='',
            form_errors={'project_name': [u'This field is required.']}
        )

    def test_blank_project_description(self):
        self._test_allocation(
            project_description='',
            form_errors={'project_description': [u'This field is required.']}
        )

    def test_blank_geographic_requirements(self):
        self._test_allocation(
            geographic_requirements='',
        )

    def test_blank_use_case(self):
        self._test_allocation(
            use_case='',
            form_errors={'use_case': [u'This field is required.']}
        )

    def test_request_quotas_ok(self):
        response = self.client.get(
            reverse('horizon:allocation:request:request'))
        self.assertStatusCode(response, 200)
        quota_specs = [
            common.quota_spec('compute', 'instances', requested_quota=1),
            common.quota_spec('compute', 'cores', requested_quota=2),
        ]
        expected_model, form = common.request_allocation(
            user=self.user, quota_specs=quota_specs)

        response = self.client.post(
            reverse('horizon:allocation:request:request'),
            form)

        # If there are no warnings, we are redirected back to the index
        # of our requests.
        self.assertStatusCode(response, 302)
        self.assertTrue(response.get('location').endswith(
            reverse('horizon:allocation:user_requests:index')),
            msg="incorrect redirect location")
        model = (models.AllocationRequest.objects
                 .get(project_description=form['project_description'],
                      parent_request_id=None))
        self.assert_allocation(model, **expected_model)

    def test_request_quotas_warn(self):
        response = self.client.get(
            reverse('horizon:allocation:request:request'))
        self.assertStatusCode(response, 200)
        quota_specs = [
            common.quota_spec('compute', 'instances', requested_quota=2),
            common.quota_spec('compute', 'cores', requested_quota=1),
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

        # redirect means success; see above
        self.assertStatusCode(response, 302)
        self.assertTrue(response.get('location').endswith(
            reverse('horizon:allocation:user_requests:index')),
            msg="incorrect redirect location")
        model = (models.AllocationRequest.objects
                 .get(project_description=form['project_description'],
                      parent_request_id=None))
        self.assert_allocation(model, **expected_model)
