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

from nectar_dashboard.rcallocation.allocation import forms
from nectar_dashboard.rcallocation.tests import base


class AllocationApproveFormTestCase(base.BaseTestCase):
    def test_fields(self):
        form = forms.AllocationApproveForm()
        self.assertCountEqual(
            [
                'status_explanation',
                'project_name',
                'project_description',
                'estimated_project_duration',
                'national',
                'bundle',
                'ignore_warnings',
                'associated_site',
                'special_approval',
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


class AllocationRejectFormTestCase(base.BaseTestCase):
    def test_fields(self):
        form = forms.AllocationRejectForm()
        self.assertCountEqual(
            ['project_name', 'project_description', 'status_explanation'],
            list(form.fields.keys()),
        )


class EditNotesFormTestCase(base.BaseTestCase):
    def test_fields(self):
        form = forms.EditNotesForm()
        self.assertCountEqual(['notes'], list(form.fields.keys()))
