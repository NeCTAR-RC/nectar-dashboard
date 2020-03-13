from django.urls import reverse

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

    def test_approve_request(self):
        # Prep a record in 'E' state
        model, form = common.request_allocation(user=self.user)
        form['ignore_warnings'] = True
        response = self.client.post(
            reverse('horizon:allocation:request:request'),
            form)
        self.assertStatusCode(response, 302)
        self.assertTrue(response.get('location').endswith(
            reverse('horizon:allocation:user_requests:index')),
            msg="incorrect redirect location")
        allocation = models.AllocationRequest.objects.get(
            project_description=form['project_description'],
            parent_request_id=None)
        self.assertEqual('E', allocation.status)

        print(models.AllocationRequest.objects.filter(
            project_description=form['project_description']).count())

        # Check we can get the approve form
        url = reverse('horizon:allocation:requests:approve_request',
                      args=(allocation.id,))
        response = self.client.get(url)
        self.assertStatusCode(response, 200)

        # Rebuild the form ... because the formset ids need to change
        model, form = common.request_allocation(user=self.user,
                                                model=allocation)

        # Submit the approve form
        form['associated_site'] = common.get_site('uom').id
        form['is_national'] = True
        form['ignore_warnings'] = True
        response = self.client.post(url, form)
        self.assertStatusCode(response, 302)
        self.assertEqual("../../", response.get('location'))

        allocation = models.AllocationRequest.objects.get(id=allocation.id)
        self.assertEqual('A', allocation.status)

        print(models.AllocationRequest.objects.filter(
            parent_request_id=allocation.id).count())

        # Submit the approval again.  This needs to fail!
        response = self.client.post(url, form)
        self.assertStatusCode(response, 302)
        self.assertEqual("../../", response.get('location'))

        allocation = models.AllocationRequest.objects.get(id=allocation.id)
        self.assertEqual('A', allocation.status)

        print(models.AllocationRequest.objects.filter(
            parent_request_id=allocation.id).count())

        # In fact, it is currently succeeding, and creating a history
        # record as well.  Bingo!
