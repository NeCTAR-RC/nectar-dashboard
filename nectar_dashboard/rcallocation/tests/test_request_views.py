from django.conf import settings
from django.core.urlresolvers import reverse

from openstack_dashboard.test.helpers import TestCase
from nectar_dashboard.rcallocation import models
from .common import request_allocation

from nectar_dashboard.rcallocation.tests import factories

class RequestTestCase(TestCase):

    def setUp(self):
        super(RequestTestCase, self).setUp()
        melbourne = factories.ZoneFactory(name='melbourne')
        monash = factories.ZoneFactory(name='monash')
        nectar = factories.ZoneFactory(name='nectar')

        volume_st = factories.ServiceTypeFactory(catalog_name='volume')
        object_st = factories.ServiceTypeFactory(catalog_name='object')
        compute_st = factories.ServiceTypeFactory(catalog_name='compute')
        volume_st.zones.add(melbourne)
        volume_st.zones.add(monash)
        object_st.zones.add(nectar)
        compute_st.zones.add(nectar)

        factories.ResourceFactory(quota_name='object', service_type=object_st)
        factories.ResourceFactory(quota_name='gigabytes',
                                  service_type=volume_st)
        factories.ResourceFactory(quota_name='cores', service_type=compute_st)

    def assert_allocation(self, model, quotas=[],
                          institutions=[], publications=[],
                          grants=[], investigators=[], **attributes):

        for field, value in attributes.items():
            self.assertEqual(getattr(model, field), value)
        self.assertEqual(model.contact_email, self.user.name)
        quotas_l = models.Quota.objects.filter(group__allocation=model)
        self.assertEqual(quotas_l.count(), len(quotas))
        for i, quota_model in enumerate(quotas_l):
            self.assertEqual(quota_model.resource.id, quotas[i]['resource'])
            self.assertEqual(quota_model.group.zone.name, quotas[i]['zone'])
            self.assertEqual(quota_model.requested_quota,
                             quotas[i]['requested_quota'])
            self.assertEqual(quota_model.quota, quotas[i]['quota'])

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
                 .get(project_description=form['project_description'],
                      parent_request_id=None))
        self.assert_allocation(model, **expected_model)

    def _test_allocation(self, form_errors={},
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

        if form_errors:
            # No redirect invalid fields
            assert response.status_code == 200
            assert response.context['form'].errors == form_errors

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
