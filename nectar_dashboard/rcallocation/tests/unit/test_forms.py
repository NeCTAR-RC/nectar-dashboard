
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
from nectar_dashboard.rcallocation.grant_type import GRANT_SUBTYPES
from nectar_dashboard.rcallocation.grant_type import GRANT_TYPES
from nectar_dashboard.rcallocation.tests import common
from nectar_dashboard.rcallocation.tests import factories


class FormsTestCase(helpers.TestCase):

    def setUp(self):
        super().setUp()
        common.factory_setup()
        self.allocation = factories.AllocationFactory.create(
            contact_email='other@example.com')

    def test_validating_base_allocation_form(self):
        form = forms.BaseAllocationForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['project_description',
                           'estimated_project_duration',
                           'use_case', 'estimated_number_users',
                           'for_percentage_1', 'for_percentage_2',
                           'for_percentage_3', 'usage_types']
        self.assertEqual(len(required_fields), len(form.errors))
        for field in required_fields:
            if field == 'usage_types':
                self.assertEqual(['Please check one or more of the above'],
                                 form.errors[field])
            else:
                self.assertEqual(['This field is required.'],
                                 form.errors[field])

    def test_validating_grant_form(self):
        form = forms.GrantForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['allocation', 'grant_type', 'grant_subtype',
                           'first_year_funded', 'last_year_funded',
                           'total_funding']
        self.assertEqual(len(required_fields), len(form.errors))
        for field in required_fields:
            self.assertEqual(['This field is required.'], form.errors[field])

    def test_validating_grant_types(self):
        # ARC grant conditionality
        form = forms.GrantForm(data={'grant_type': 'arc',
                                     'grant_subtype': 'unspecified'})
        self.assertEqual(['Select an ARC grant subtype for this grant'],
                         form.errors['grant_subtype'])

        form = forms.GrantForm(data={'grant_type': 'arc',
                                     'grant_subtype': 'arc-discovery'})
        self.assertIsNone(form.errors.get('grant_subtype'))
        self.assertEqual(['Enter the ARC grant id for this grant'],
                         form.errors.get('grant_id'))

        form = forms.GrantForm(data={'grant_type': 'arc',
                                     'grant_subtype': 'arc-other'})
        self.assertIsNone(form.errors.get('grant_subtype'))
        self.assertIsNone(form.errors.get('grant_id'))
        self.assertEqual(['Provide details for this grant'],
                         form.errors.get('funding_body_scheme'))

        # NHMRC grant conditionality
        form = forms.GrantForm(data={'grant_type': 'nhmrc',
                                     'grant_subtype': 'unspecified'})
        self.assertEqual(['Select an NHMRC grant subtype for this grant'],
                         form.errors['grant_subtype'])

        form = forms.GrantForm(data={'grant_type': 'nhmrc',
                                     'grant_subtype': 'nhmrc-investigator'})
        self.assertIsNone(form.errors.get('grant_subtype'))
        self.assertEqual(['Enter the NHMRC grant id for this grant'],
                         form.errors.get('grant_id'))

        form = forms.GrantForm(data={'grant_type': 'nhmrc',
                                     'grant_subtype': 'nhmrc-other'})
        self.assertIsNone(form.errors.get('grant_subtype'))
        self.assertIsNone(form.errors.get('grant_id'))
        self.assertEqual(['Provide details for this grant'],
                         form.errors.get('funding_body_scheme'))

        # State grant conditionality
        STATES = ['act', 'nsw', 'nt', 'qld', 'sa', 'tas', 'vic', 'wa']
        for subtype in GRANT_SUBTYPES:
            form = forms.GrantForm(data={'grant_type': 'state',
                                         'grant_subtype': subtype[0]})
            if subtype[0] in STATES:
                self.assertIsNone(form.errors.get('grant_subtype'))
            else:
                self.assertEqual(['Select the State for this grant'],
                                 form.errors.get('grant_subtype'))
            self.assertIsNone(form.errors.get('grant_id'))
            self.assertEqual(['Provide details for this grant'],
                             form.errors.get('funding_body_scheme'))

        # Other grant conditionality
        for type in GRANT_TYPES:
            if type[0] in ['arc', 'nhmrc', 'state']:
                continue
            form = forms.GrantForm(data={'grant_type': type[0],
                                         'grant_subtype': 'unspecified'})
            self.assertIsNone(form.errors.get('grant_id'))
            self.assertEqual(['Provide details for this grant'],
                             form.errors.get('funding_body_scheme'))

        # Forbidden grant type / subtype combinations
        for type in GRANT_TYPES:
            for subtype in GRANT_SUBTYPES:
                form = forms.GrantForm(data={'grant_type': type[0],
                                             'grant_subtype': subtype[0]})
                allowed = ((type[0] == 'arc'
                            and subtype[0].startswith('arc-'))
                           or (type[0] == 'nhmrc'
                               and subtype[0].startswith('nhmrc-'))
                           or (type[0] == 'state' and subtype[0] in STATES)
                           or (type[0] not in ['arc', 'nhmrc', 'state']
                               and subtype[0] == 'unspecified'))
                if allowed:
                    self.assertIsNone(form.errors.get('grant_subtype'))
                else:
                    self.assertIsNotNone(form.errors.get('grant_subtype'))

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
        self.assertNotIn('doi', form.cleaned_data)

        # Malformed DOI (according to us)
        form = forms.PublicationForm(data={
            'publication': 'Mary had a little lamb',
            'doi': 'doi:10.01000/ABC DEF',
            'allocation': self.allocation.id})
        form.is_valid()
        self.assertNotIn('doi', form.cleaned_data)

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
