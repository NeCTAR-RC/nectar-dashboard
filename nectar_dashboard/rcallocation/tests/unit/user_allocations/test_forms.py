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

from nectar_dashboard.rcallocation.tests import base
from nectar_dashboard.rcallocation.user_allocations import forms


class UserAllocationRequestFormTestCase(base.BaseTestCase):
    def test_fields(self):
        form = forms.UserAllocationRequestForm()
        self.assertCountEqual(
            [
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
                'usage_types',
                'national',
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


class UserAllocationRequestAmendFormTestCase(base.BaseTestCase):
    def test_fields(self):
        form = forms.UserAllocationRequestAmendForm()
        self.assertCountEqual(
            [
                'project_name',
                'project_description',
                'contact_email',
                'estimated_project_duration',
                'use_case',
                'usage_patterns',
                'geographic_requirements',
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
                'usage_types',
                'supported_organisations',
                'nectar_benefit_description',
                'nectar_research_impact',
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
