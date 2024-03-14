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

from nectar_dashboard.rcallocation.request import forms
from nectar_dashboard.rcallocation.tests import base


class UserAllocationRequestFormTestCase(base.BaseTestCase):

    def test_fields(self):
        form = forms.UserAllocationRequestForm()
        self.assertCountEqual(['project_name',
                               'project_description',
                               'contact_email',
                               'estimated_project_duration',
                               'convert_trial_project',
                               'use_case',
                               'usage_patterns',
                               'geographic_requirements',
                               'estimated_number_users',
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
                               'quota-volume.gigabytes__tas'],
                         list(form.fields.keys()))
