from unittest import mock

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

    @mock.patch('nectar_dashboard.rcallocation.notifier.FreshdeskNotifier',
                new=base.FAKE_FD_NOTIFIER_CLASS)
    def test_approve_request(self):
        base.FAKE_FD_NOTIFIER.send_email.reset_mock()

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

        # Check we can get the approval page
        url = reverse('horizon:allocation:requests:approve_request',
                      args=(allocation.id,))
        response = self.client.get(url)
        self.assertStatusCode(response, 200)

        # Rebuild the form ... because the formset ids need to change
        model, form = common.request_allocation(user=self.user,
                                                model=allocation)

        # Submit the approval form
        form['associated_site'] = common.get_site('uom').id
        form['is_national'] = True
        form['ignore_warnings'] = True
        response = self.client.post(url, form)
        self.assertStatusCode(response, 302)
        self.assertEqual("../../", response.get('location'))

        allocation = models.AllocationRequest.objects.get(id=allocation.id)
        self.assertEqual('A', allocation.status)

        self.assertEqual(1,
                         models.AllocationRequest.objects.filter(
            parent_request_id=allocation.id).count())

        # Submit the approval again: simulate double approve.
        # This should fail
        response = self.client.post(url, form)
        self.assertStatusCode(response, 400)

        self.assertEqual(1,
                         models.AllocationRequest.objects.filter(
            parent_request_id=allocation.id).count())

        base.FAKE_FD_NOTIFIER.send_email.assert_called_once()
        call_kwargs = base.FAKE_FD_NOTIFIER.send_email.mock_calls[0].kwargs
        self.assertEqual("test_user", call_kwargs['email'])
        self.assertEqual(
            f"Allocation request [{allocation.project_description}]",
            call_kwargs['subject'])
        # Not checking the expansion of the template body.
