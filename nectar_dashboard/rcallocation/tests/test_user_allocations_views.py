from django.core.urlresolvers import reverse
from django.utils.importlib import import_module  # noqa

from nectar_dashboard.rcallocation import models
from openstack_dashboard.test.helpers import TestCase

from .factories import AllocationFactory
from .common import allocation_to_dict, request_allocation


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
        for i, grant_model in enumerate(grants_l):
            assert grant_model.grant_type == grants[i]['grant_type']

        investigators_l = model.investigators.all()
        for i, investigator_model in enumerate(investigators_l):
            assert investigator_model.email == investigators[i]['email']

    def test_edit_allocation_request(self):

        allocation = AllocationFactory.create(contact_email=self.user.name)
        initial_state = allocation_to_dict(
            models.AllocationRequest.objects.get(pk=allocation.pk))

        response = self.client.get(
            reverse('horizon:allocation:user_requests:edit_request',
                    args=(allocation.id,)))
        assert response.status_code == 200
        expected_model, form = request_allocation(user=self.user,
                                                  model=allocation)

        response = self.client.post(
            reverse('horizon:allocation:user_requests:edit_request',
                    args=(allocation.id,)),
            form)

        # Check to make sure we were redirected back to the index of
        # our requests.
        assert response.status_code == 302
        assert response.get('location').endswith(
            reverse('horizon:allocation:user_requests:index'))
        model = (models.AllocationRequest.objects.get(
            project_name=form['project_name'],
            parent_request_id=None))
        self.assert_allocation(model, **expected_model)

        # check historical allocation model
        old_model = (models.AllocationRequest.objects.get(
            parent_request_id=model.id))
        old_state = allocation_to_dict(old_model)

        # some fields are changed during the archive process, these
        # fields should not be compared.
        for invalid_field in ['modified_time', 'id', 'parent_request']:
            del old_state[invalid_field]
            del initial_state[invalid_field]
        for quota in old_state['quota'] + initial_state['quota']:
            del quota['id']
            del quota['allocation']

        assert old_state == initial_state
