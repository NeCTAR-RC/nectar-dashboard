from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.importlib import import_module  # noqa

from openstack_dashboard.test.helpers import TestCase
from nectar_dashboard.rcallocation import models
from .common import request_allocation


class RequestTestCase(TestCase):

    def assert_allocation(self, model, quotas=[],
                          institutions=[], publications=[],
                          grants=[], investigators=[], **attributes):

        for field, value in attributes.items():
            assert getattr(model, field) == value
        assert model.contact_email == self.user.name
        quotas_l = model.quotas.all()
        for i, quota_model in enumerate(quotas_l):
            assert quota_model.zone == quotas[i]['zone']
            assert quota_model.resource == quotas[i]['resource']
            assert quota_model.requested_quota == quotas[i]['requested_quota']
            assert quota_model.quota == quotas[i]['quota']

        institutions_l = model.institutions.all()
        for i, institution_model in enumerate(institutions_l):
            assert institution_model.name == institutions[i]['name']

        publications_l = model.publications.all()
        for i, pub_model in enumerate(publications_l):
            assert pub_model.publication == publications[i]['publication']

        grants_l = model.grants.all()
        for i, g_model in enumerate(grants_l):
            assert g_model.grant_type == grants[i]['grant_type']
            assert g_model.funding_body_scheme == grants[i][
                'funding_body_scheme']
            assert g_model.grant_id == grants[i]['grant_id']
            assert g_model.first_year_funded == grants[i]['first_year_funded']
            assert g_model.total_funding == grants[i]['total_funding']

        investigators_l = model.investigators.all()
        for i, inv_m in enumerate(investigators_l):
            assert inv_m.title == investigators[i]['title']
            assert inv_m.given_name == investigators[i]['given_name']
            assert inv_m.surname == investigators[i]['surname']
            assert inv_m.email == investigators[i]['email']
            assert inv_m.institution == investigators[i]['institution']
            assert inv_m.additional_researchers == investigators[i][
                'additional_researchers']

    def _test_request_allocation(self):
        response = self.client.get(
            reverse('horizon:allocation:request:request'))
        self.assertStatusCode(response, 200)
        expected_model, form = request_allocation(user=self.user)
        response = self.client.post(
            reverse('horizon:allocation:request:request'),
            form)

        # Check to make sure we were redirected back to the index of
        # our requests.
        self.assertStatusCode(response, 302)
        assert response.get('location').endswith(
            reverse('horizon:allocation:user_requests:index'))

        model = (models.AllocationRequest.objects
                 .get(project_name=form['project_name'],
                      parent_request_id=None))
        self.assert_allocation(model, **expected_model)

    def _test_allocation(self, form_errors={},
                         quotaFormSet_errors=[{}, {}, {}],
                         **kwargs):
        response = self.client.get(
            reverse('horizon:allocation:request:request'))
        expected_model, form = request_allocation(user=self.user)
        backup_values = {}

        for field, value in kwargs.items():
            assert field in form
            backup_values[field] = form[field]
            form[field] = value

        response = self.client.post(
            reverse('horizon:allocation:request:request'),
            form)

        if form_errors or any(quotaFormSet_errors):
            # No redirect invalid fields
            assert response.status_code == 200
            assert response.context['form'].errors == form_errors
            assert (response.context['quotaFormSet'].errors ==
                    quotaFormSet_errors)

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
        assert response.status_code == 302
        assert response.get('location').endswith(
            reverse('horizon:allocation:user_requests:index'))

        model = (models.AllocationRequest.objects
                 .get(project_name=form['project_name'],
                      parent_request_id=None))
        self.assert_allocation(model, **expected_model)

    def _test_blank_tenant_name(self):
        self._test_allocation(
            tenant_name='',
            form_errors={'tenant_name': [u'This field is required.']}
        )

    def _test_blank_project_name(self):
        self._test_allocation(
            project_name='',
            form_errors={'project_name': [u'This field is required.']}
        )

    def _test_blank_geographic_requirements(self):
        self._test_allocation(
            geographic_requirements='',
        )

    def _test_blank_use_case(self):
        self._test_allocation(
            use_case='',
            form_errors={'use_case': [u'This field is required.']}
        )
