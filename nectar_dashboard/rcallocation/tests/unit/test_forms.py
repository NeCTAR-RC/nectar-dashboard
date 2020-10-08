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

from openstack_dashboard.test import helpers

from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories


class FormsTestCase(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.factory_setup()
        self.allocation = factories.AllocationFactory.create(
            contact_email='other@example.com')

    def test_validating_doi(self):
        # No DOI is OK
        form = forms.PublicationForm(data={
            'publication': 'Mary had a little lamb',
            'allocation': self.allocation.id})
        form.is_valid()
        self.assertIsNone(form.cleaned_data['doi'])

        # DOI is OK
        form = forms.PublicationForm(data={
            'publication': 'Mary had a little lamb',
            'doi': '10.01000/ABCDEF',
            'allocation': self.allocation.id})
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '10.01000/ABCDEF')

        # Quietly remove a "doi:" prefix
        form = forms.PublicationForm(data={
            'publication': 'Mary had a little lamb',
            'doi': 'doi:10.01000/ABCDEF',
            'allocation': self.allocation.id})
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '10.01000/ABCDEF')

        # Malformed DOI
        form = forms.PublicationForm(data={
            'publication': 'Mary had a little lamb',
            'doi': 'ABCDEF',
            'allocation': self.allocation.id})
        form.is_valid()
        self.assertTrue('doi' not in form.cleaned_data)

        # Malformed DOI (according to us)
        form = forms.PublicationForm(data={
            'publication': 'Mary had a little lamb',
            'doi': 'doi:10.01000/ABC DEF',
            'allocation': self.allocation.id})
        form.is_valid()
        self.assertTrue('doi' not in form.cleaned_data)

        # Trailing whitespace should be trimmed
        form = forms.PublicationForm(data={
            'publication': 'Mary had a little lamb',
            'doi': '10.01000/ABCDEF ',
            'allocation': self.allocation.id})
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '10.01000/ABCDEF')

        # Quietly remove an http resolver URL
        form = forms.PublicationForm(data={
            'publication': 'Mary had a little lamb',
            'doi': 'http://doi.org/10.01000/ABCDEF',
            'allocation': self.allocation.id})
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '10.01000/ABCDEF')

        # Quietly remove an https resolver URL
        form = forms.PublicationForm(data={
            'publication': 'Mary had a little lamb',
            'doi': 'https://doi.pangea.de/10so_me-thing/10.01000/ABCDEF',
            'allocation': self.allocation.id})
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '10.01000/ABCDEF')
