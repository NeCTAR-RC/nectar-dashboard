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

from nectar_dashboard.rcallocation import forms
from nectar_dashboard.rcallocation.grant_type import GRANT_SUBTYPES
from nectar_dashboard.rcallocation.grant_type import GRANT_TYPES
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import output_type_choices
from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.tests import factories


DUMMY_ALLOC_DATA = {
    'project_description': 'dummy',
    'project_name': 'dummy',
    'estimated_project_duration': 1,
    'use_case': 'dummy',
    'multiple_allocations_check': True,
    'users_figure_type': 'measured',
    'for_percentage_1': 0,
    'for_percentage_2': 0,
    'for_percentage_3': 0,
    'usage_types': ['Other'],
    'supported_organisations': [1],
}


class FormsTestCase(base.BaseTestCase):
    def setUp(self):
        super().setUp()
        self.allocation = factories.AllocationFactory.create(
            contact_email='other@example.com'
        )


class BaseAllocationFormTestCase(FormsTestCase):
    def test_fields(self):
        form = forms.BaseAllocationForm()
        self.assertCountEqual(
            [
                'status_explanation',
                'project_name',
                'project_description',
                'contact_email',
                'estimated_project_duration',
                'convert_trial_project',
                'use_case',
                'usage_patterns',
                'geographic_requirements',
                'direct_access_user_estimate',
                'estimated_service_count',
                'estimated_service_active_users',
                'direct_access_user_past_year',
                'active_service_count',
                'service_active_users_past_year',
                'users_figure_type',
                'multiple_allocations_check',
                'field_of_research_1',
                'for_percentage_1',
                'field_of_research_2',
                'for_percentage_2',
                'field_of_research_3',
                'for_percentage_3',
                'ardc_support',
                'ardc_explanation',
                'ncris_explanation',
                'ncris_facilities',
                'nectar_benefit_description',
                'nectar_research_impact',
                'national',
                'usage_types',
                'supported_organisations',
                'bundle',
                'ignore_warnings',
            ],
            list(form.fields.keys()),
        )

    def test_validating_base_allocation_form(self):
        form = forms.BaseAllocationForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = [
            'project_description',
            'estimated_project_duration',
            'use_case',
            'users_figure_type',
            'for_percentage_1',
            'for_percentage_2',
            'for_percentage_3',
            'usage_types',
            'supported_organisations',
        ]
        self.assertEqual(len(required_fields), len(form.errors))
        for field in required_fields:
            if field == 'usage_types':
                self.assertEqual(
                    ['Please check one or more of the above'],
                    form.errors[field],
                )
            else:
                self.assertEqual(
                    ['This field is required.'], form.errors[field]
                )
        form = forms.BaseAllocationForm(data=DUMMY_ALLOC_DATA)
        self.assertTrue(form.is_valid())

    def test_validating_survey_types(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['usage_types'] = ['Rubbish']

        form = forms.BaseAllocationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            [
                'Select a valid choice. Rubbish is '
                'not one of the available choices.'
            ],
            form.errors['usage_types'],
        )

        data = DUMMY_ALLOC_DATA.copy()
        data['usage_types'] = ['Disabled', 'Other']

        form = forms.BaseAllocationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            [
                'Select a valid choice. Disabled is '
                'not one of the available choices.'
            ],
            form.errors['usage_types'],
        )

    def test_validating_project_name(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['project_name'] = 'pt-10001'

        form = forms.BaseAllocationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            ["Project names cannot start with 'pt-'"],
            form.errors['project_name'],
        )

        data['project_name'] = 'pt_10001'
        form = forms.BaseAllocationForm(data=data)
        self.assertTrue(form.is_valid())


class AllocationRequestFormTestCase(FormsTestCase):
    def test_fields(self):
        form = forms.AllocationRequestForm()
        self.assertCountEqual(
            [
                'status_explanation',
                'project_name',
                'project_description',
                'contact_email',
                'estimated_project_duration',
                'convert_trial_project',
                'use_case',
                'usage_patterns',
                'geographic_requirements',
                'multiple_allocations_check',
                'direct_access_user_estimate',
                'estimated_service_count',
                'estimated_service_active_users',
                'field_of_research_1',
                'for_percentage_1',
                'field_of_research_2',
                'for_percentage_2',
                'field_of_research_3',
                'for_percentage_3',
                'ardc_support',
                'ardc_explanation',
                'ncris_explanation',
                'ncris_facilities',
                'national',
                'usage_types',
                'supported_organisations',
                'bundle',
                'ignore_warnings',
                'quota-compute.cores__nectar',
                'quota-compute.instances__nectar',
                'quota-rating.budget__nectar',
                'quota-object.object__nectar',
                'quota-network.router__nectar',
                'quota-network.network__nectar',
                'quota-network.loadbalancer__nectar',
                'quota-network.floatingip__nectar',
                'quota-volume.gigabytes__monash',
                'quota-volume.gigabytes__melbourne',
                'quota-volume.gigabytes__tas',
            ],
            list(form.fields.keys()),
        )

    def test_validating_project_name(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['project_name'] = 'pt_10001'

        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            ['Must not start with "pt-" or similar.'],
            form.errors['project_name'],
        )

        data['project_name'] = 'PT_10001'
        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            ['Must not start with "pt-" or similar.'],
            form.errors['project_name'],
        )

        data['project_name'] = 'abc'
        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            ['Between 5 and 32 characters required.'],
            form.errors['project_name'],
        )

        data['project_name'] = '-abcdef'
        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            [
                'Letters, numbers, underscore and hyphens '
                'only. Must start with a letter.'
            ],
            form.errors['project_name'],
        )

        data['project_name'] = '123-abc'
        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            [
                'Letters, numbers, underscore and hyphens '
                'only. Must start with a letter.'
            ],
            form.errors['project_name'],
        )

        data['project_name'] = 'abc[123]'
        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            [
                'Letters, numbers, underscore and hyphens '
                'only. Must start with a letter.'
            ],
            form.errors['project_name'],
        )

        data['project_name'] = 'abc-123'
        form = forms.AllocationRequestForm(data=data)
        self.assertTrue(form.is_valid())

    def test_user_estimate_not_multiple_required(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['multiple_allocations_check'] = False
        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            ['This field is required'],
            form.errors['direct_access_user_estimate'],
        )
        self.assertEqual(
            ['This field is required'], form.errors['estimated_service_count']
        )
        self.assertEqual(
            ['This field is required'],
            form.errors['estimated_service_active_users'],
        )

    def test_validating_facilities_unwanted_explanation(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['ncris_explanation'] = 'something'
        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertNotIn('ncris_explanation', form.cleaned_data)
        self.assertEqual(
            [
                'No NCRIS Facilities have been selected: '
                'choose one or more, or remove the '
                'explanation text.'
            ],
            form.errors['ncris_explanation'],
        )

    def test_validating_facilities_no_explanation_required(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['ncris_facilities'] = ['ALA']
        form = forms.AllocationRequestForm(data=data)
        self.assertTrue(form.is_valid())

    def test_validating_facilities_explanation_required(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['ncris_facilities'] = ['Other']
        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            [
                "More details are required when you include "
                "'Pilot' or 'Other' above."
            ],
            form.errors['ncris_explanation'],
        )

    def test_validating_facilities_explanation_allowed(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['ncris_facilities'] = ['Other']
        data['ncris_explanation'] = 'something'
        form = forms.AllocationRequestForm(data=data)
        self.assertTrue(form.is_valid())

    def test_validating_supports_unwanted_explanation(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['ardc_explanation'] = 'something'
        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertNotIn('ardc_explanation', form.cleaned_data)
        self.assertEqual(
            [
                "No ARDC projects or programs have been selected: "
                "choose one or more, or remove the explanation "
                "text."
            ],
            form.errors['ardc_explanation'],
        )

    def test_validating_supports_no_explanation_required(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['ardc_support'] = ['CVL']
        form = forms.AllocationRequestForm(data=data)
        self.assertTrue(form.is_valid())

    def test_validating_supports_explanation_required(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['ardc_support'] = ['ANDS']
        form = forms.AllocationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            [
                "Add details for the ARDC support that you "
                "are claiming for your request."
            ],
            form.errors['ardc_explanation'],
        )

    def test_validating_supports_explanation_allowed(self):
        data = DUMMY_ALLOC_DATA.copy()
        data['ardc_support'] = ['CVL']
        data['ardc_explanation'] = 'something'
        form = forms.AllocationRequestForm(data=data)
        self.assertTrue(form.is_valid())


class ChiefInvestigatorFormTestCase(FormsTestCase):
    def test_fields(self):
        form = forms.ChiefInvestigatorForm()
        self.assertCountEqual(
            [
                'allocation',
                'title',
                'given_name',
                'surname',
                'email',
                'primary_organisation',
                'additional_researchers',
            ],
            list(form.fields.keys()),
        )

    def test_validating_ci_form_missing(self):
        form = forms.ChiefInvestigatorForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = [
            'allocation',
            'title',
            'primary_organisation',
            'surname',
            'email',
            'given_name',
        ]
        self.assertEqual(len(required_fields), len(form.errors))
        for field in required_fields:
            self.assertEqual(['This field is required.'], form.errors[field])

    def test_validating_ci_form(self):
        form = forms.ChiefInvestigatorForm(
            data={
                'allocation': 1,
                'title': 'demigod',
                'primary_organisation': 1,
                'surname': 'McYadda',
                'email': 'yadda@yadda.com',
                'given_name': 'Yadda',
            }
        )
        self.assertTrue(form.is_valid())

    def test_validating_ci_form_disabled_org(self):
        disabled = factories.OrganisationFactory.create(enabled=False)
        form = forms.ChiefInvestigatorForm(
            data={
                'allocation': 1,
                'title': 'demigod',
                'primary_organisation': disabled.id,
                'surname': 'McYadda',
                'email': 'yadda@yadda.com',
                'given_name': 'Yadda',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertRegex(
            str(form.errors['primary_organisation']), ".+not.+valid.+"
        )

    def test_validating_ci_form_all_org(self):
        all = models.Organisation.objects.get(
            full_name=models.ORG_ALL_FULL_NAME
        )
        form = forms.ChiefInvestigatorForm(
            data={
                'allocation': 1,
                'title': 'demigod',
                'primary_organisation': all.id,
                'surname': 'McYadda',
                'email': 'yadda@yadda.com',
                'given_name': 'Yadda',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertRegex(
            str(form.errors['primary_organisation']), ".+not.+meaningful.+"
        )


class GrantFormTestCase(FormsTestCase):
    def test_fields(self):
        form = forms.GrantForm()
        self.assertCountEqual(
            [
                'grant_type',
                'grant_subtype',
                'funding_body_scheme',
                'grant_id',
                'first_year_funded',
                'last_year_funded',
                'total_funding',
                'allocation',
            ],
            list(form.fields.keys()),
        )

    def test_validating_grant_form(self):
        form = forms.GrantForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = [
            'allocation',
            'grant_type',
            'grant_subtype',
            'first_year_funded',
            'last_year_funded',
            'total_funding',
        ]
        self.assertEqual(len(required_fields), len(form.errors))
        for field in required_fields:
            self.assertEqual(['This field is required.'], form.errors[field])

    def test_validating_grant_types(self):
        # ARC grant conditionality
        form = forms.GrantForm(
            data={'grant_type': 'arc', 'grant_subtype': 'unspecified'}
        )
        self.assertEqual(
            ['Select an ARC grant subtype for this grant'],
            form.errors['grant_subtype'],
        )

        form = forms.GrantForm(
            data={'grant_type': 'arc', 'grant_subtype': 'arc-discovery'}
        )
        self.assertIsNone(form.errors.get('grant_subtype'))
        self.assertEqual(
            ['Enter the ARC grant id for this grant'],
            form.errors.get('grant_id'),
        )

        form = forms.GrantForm(
            data={'grant_type': 'arc', 'grant_subtype': 'arc-other'}
        )
        self.assertIsNone(form.errors.get('grant_subtype'))
        self.assertIsNone(form.errors.get('grant_id'))
        self.assertEqual(
            ['Provide details for this grant'],
            form.errors.get('funding_body_scheme'),
        )

        # NHMRC grant conditionality
        form = forms.GrantForm(
            data={'grant_type': 'nhmrc', 'grant_subtype': 'unspecified'}
        )
        self.assertEqual(
            ['Select an NHMRC grant subtype for this grant'],
            form.errors['grant_subtype'],
        )

        form = forms.GrantForm(
            data={'grant_type': 'nhmrc', 'grant_subtype': 'nhmrc-investigator'}
        )
        self.assertIsNone(form.errors.get('grant_subtype'))
        self.assertEqual(
            ['Enter the NHMRC grant id for this grant'],
            form.errors.get('grant_id'),
        )

        form = forms.GrantForm(
            data={'grant_type': 'nhmrc', 'grant_subtype': 'nhmrc-other'}
        )
        self.assertIsNone(form.errors.get('grant_subtype'))
        self.assertIsNone(form.errors.get('grant_id'))
        self.assertEqual(
            ['Provide details for this grant'],
            form.errors.get('funding_body_scheme'),
        )

        # RDCC grant conditionality
        form = forms.GrantForm(
            data={'grant_type': 'rdc', 'grant_subtype': 'unspecified'}
        )
        self.assertEqual(
            ['Select an RDC grant subtype for this grant'],
            form.errors['grant_subtype'],
        )

        form = forms.GrantForm(
            data={'grant_type': 'rdc', 'grant_subtype': 'rdc-ael'}
        )
        self.assertIsNone(form.errors.get('grant_subtype'))
        self.assertIsNone(form.errors.get('grant_id'))
        self.assertEqual(
            ['Provide details for this grant ' 'or a grant id (below!)'],
            form.errors.get('funding_body_scheme'),
        )

        # State grant conditionality
        STATES = ['act', 'nsw', 'nt', 'qld', 'sa', 'tas', 'vic', 'wa']
        for subtype in GRANT_SUBTYPES:
            form = forms.GrantForm(
                data={'grant_type': 'state', 'grant_subtype': subtype[0]}
            )
            if subtype[0] in STATES:
                self.assertIsNone(form.errors.get('grant_subtype'))
            else:
                self.assertEqual(
                    ['Select the State for this grant'],
                    form.errors.get('grant_subtype'),
                )
            self.assertIsNone(form.errors.get('grant_id'))
            self.assertEqual(
                ['Provide details for this grant'],
                form.errors.get('funding_body_scheme'),
            )

        # Other grant conditionality
        for type in GRANT_TYPES:
            if type[0] in ['arc', 'nhmrc', 'rdc', 'state']:
                continue
            form = forms.GrantForm(
                data={'grant_type': type[0], 'grant_subtype': 'unspecified'}
            )
            self.assertIsNone(form.errors.get('grant_id'))
            self.assertEqual(
                ['Provide details for this grant'],
                form.errors.get('funding_body_scheme'),
            )

        # Forbidden grant type / subtype combinations
        for type in GRANT_TYPES:
            for subtype in GRANT_SUBTYPES:
                form = forms.GrantForm(
                    data={'grant_type': type[0], 'grant_subtype': subtype[0]}
                )
                allowed = (
                    (type[0] == 'arc' and subtype[0].startswith('arc-'))
                    or (type[0] == 'nhmrc' and subtype[0].startswith('nhmrc-'))
                    or (type[0] == 'rdc' and subtype[0].startswith('rdc-'))
                    or (type[0] == 'state' and subtype[0] in STATES)
                    or (
                        type[0] not in ['arc', 'nhmrc', 'state', 'rdc']
                        and subtype[0] == 'unspecified'
                    )
                )
                if allowed:
                    self.assertIsNone(form.errors.get('grant_subtype'))
                else:
                    self.assertIsNotNone(form.errors.get('grant_subtype'))


class PublicationFormTestCase(FormsTestCase):
    def test_fields(self):
        form = forms.PublicationForm()
        self.assertCountEqual(
            [
                'output_type',
                'publication',
                'doi',
                'crossref_metadata',
                'allocation',
            ],
            list(form.fields.keys()),
        )

    def test_validating_publication_form(self):
        form = forms.PublicationForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['allocation', 'output_type']
        error_fields = [f for f in form.errors if f != '__all__']
        self.assertEqual(len(required_fields), len(error_fields))
        for field in required_fields:
            self.assertEqual(['This field is required.'], form.errors[field])

        self.assertEqual(
            [
                'No details about this research output have been '
                'provided. Provide either a DOI or citation '
                'details, as appropriate.'
            ],
            form.non_field_errors(),
        )

        pub_data = {
            'allocation': 1,
            'doi': '10.1177/0309132512437077',
            'output_type': output_type_choices.BOOK,
        }
        form = forms.PublicationForm(data=pub_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(
            [
                'Since the DOI you provided has not been validated, '
                'citation details must be entered by hand.'
            ],
            form.errors['publication'],
        )

        pub_data['crossref_metadata'] = 'gerbils'
        form = forms.PublicationForm(data=pub_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(
            [
                'Crossref_metadata not JSON. '
                'Please report this to Nectar support.'
            ],
            form.non_field_errors(),
        )

        pub_data['crossref_metadata'] = '["gerbils"]'
        form = forms.PublicationForm(data=pub_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(
            [
                'Crossref_metadata not a valid Crossref response. '
                'Please report this to Nectar support.'
            ],
            form.non_field_errors(),
        )

        pub_data['crossref_metadata'] = '{"gerbils": "OK!"}'
        form = forms.PublicationForm(data=pub_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(
            [
                'Crossref_metadata not a valid Crossref response. '
                'Please report this to Nectar support.'
            ],
            form.non_field_errors(),
        )

        pub_data['crossref_metadata'] = ''
        pub_data['output_type'] = (
            output_type_choices.PEER_REVIEWED_JOURNAL_ARTICLE
        )
        form = forms.PublicationForm(data=pub_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(
            [
                'A validated DOI is required for a peer '
                'reviewed journal article.'
            ],
            form.non_field_errors(),
        )

    def test_validating_doi(self):
        # No DOI is OK
        form = forms.PublicationForm(
            data={
                'publication': 'Mary had a little lamb',
                'allocation': self.allocation.id,
            }
        )
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '')

        # DOI is OK
        form = forms.PublicationForm(
            data={
                'publication': 'Mary had a little lamb',
                'doi': '10.01000/ABCDEF',
                'allocation': self.allocation.id,
            }
        )
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '10.01000/ABCDEF')

        # Quietly remove a "doi:" prefix
        form = forms.PublicationForm(
            data={
                'publication': 'Mary had a little lamb',
                'doi': 'doi:10.01000/ABCDEF',
                'allocation': self.allocation.id,
            }
        )
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '10.01000/ABCDEF')

        # Malformed DOI
        form = forms.PublicationForm(
            data={
                'publication': 'Mary had a little lamb',
                'doi': 'ABCDEF',
                'allocation': self.allocation.id,
            }
        )
        form.is_valid()
        self.assertNotIn('doi', form.cleaned_data)

        # Malformed DOI (according to us)
        form = forms.PublicationForm(
            data={
                'publication': 'Mary had a little lamb',
                'doi': 'doi:10.01000/ABC DEF',
                'allocation': self.allocation.id,
            }
        )
        form.is_valid()
        self.assertNotIn('doi', form.cleaned_data)

        # Trailing whitespace should be trimmed
        form = forms.PublicationForm(
            data={
                'publication': 'Mary had a little lamb',
                'doi': '10.01000/ABCDEF ',
                'allocation': self.allocation.id,
            }
        )
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '10.01000/ABCDEF')

        # Quietly remove an http resolver URL
        form = forms.PublicationForm(
            data={
                'publication': 'Mary had a little lamb',
                'doi': 'http://doi.org/10.01000/ABCDEF',
                'allocation': self.allocation.id,
            }
        )
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '10.01000/ABCDEF')

        # Quietly remove an https resolver URL
        form = forms.PublicationForm(
            data={
                'publication': 'Mary had a little lamb',
                'doi': 'https://doi.pangea.de/10so_me-thing/10.01000/ABCDEF',
                'allocation': self.allocation.id,
            }
        )
        form.is_valid()
        self.assertEqual(form.cleaned_data['doi'], '10.01000/ABCDEF')


class QuotaMixinTestCase(FormsTestCase):
    def test_generate_quota_fields(self):
        form = forms.AllocationRequestForm()
        quota_fields = [f for f in form.fields if f.startswith('quota-')]
        self.assertEqual(11, len(quota_fields))

    def test_multi_zone_quota_fields(self):
        form = forms.AllocationRequestForm()
        items = form.multi_zone_quota_fields()
        self.assertEqual(1, len(items))
        service_type, zones = list(items)[0]
        self.assertEqual('volume', service_type.catalog_name)
        # 3 zones (melbourne, monash and tas) so should be 3 fields
        self.assertEqual(3, len(zones))

        all_zones = [zone.name for zone in zones.keys()]
        all_zones.sort()
        self.assertEqual(['melbourne', 'monash', 'tas'], all_zones)
        all_fields = []
        for zone, fields in zones.items():
            all_fields += fields
        for f in all_fields:
            self.assertEqual(
                models.Resource.objects.get(quota_name='gigabytes'),
                f.field.resource,
            )

    def test_single_zone_quota_fields(self):
        form = forms.AllocationRequestForm()
        items = form.single_zone_quota_fields()
        self.assertEqual(4, len(items))
        service_types = [d[0].catalog_name for d in items]
        service_types.sort()
        self.assertEqual(
            ['compute', 'network', 'object', 'rating'], service_types
        )

        data = [d for d in items if d[0].catalog_name == 'compute']
        compute_st, fields = data[0]
        self.assertEqual('compute', compute_st.catalog_name)
        # Should be cores and instances (ram) is not requestable in tests
        self.assertEqual(2, len(fields))
