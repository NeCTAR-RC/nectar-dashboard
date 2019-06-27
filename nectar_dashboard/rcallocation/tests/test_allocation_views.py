from django.core.urlresolvers import reverse

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories


class ApproverRequestTestCase(base.BaseApproverTestCase):

    def test_edit_allocation_note_request(self):

        allocation = factories.AllocationFactory.create(
            contact_email=self.user.name)
        initial_state = common.allocation_to_dict(
            models.AllocationRequest.objects.get(pk=allocation.pk))
        self.assertTrue(allocation.notes is None)

        url = reverse('horizon:allocation:requests:edit_notes',
                      args=(allocation.id,))
        response = self.client.get(url)
        self.assertStatusCode(response, 200)

        form = {'id': allocation.id, 'notes': "This is a note"}
        response = self.client.post(url, form)

        # Check to make sure we were redirected back to (admin)
        # allocation view
        self.assertStatusCode(response, 302)
        self.assertEqual(reverse('horizon:allocation:requests:allocation_view',
                                 args=(allocation.id,)),
                         response.get('location'))

        model = models.AllocationRequest.objects.get(
            project_description=allocation.project_description,
            parent_request_id=None)
        self.assertEqual("This is a note", model.notes)
        model_state = common.allocation_to_dict(model)
        initial_state.pop('notes')
        model_state.pop('notes')
        self.assertEqual(initial_state, model_state, 
                         msg="allocation fields changed unexpectedly")
