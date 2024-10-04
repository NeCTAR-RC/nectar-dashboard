# Copyright 2019 Australian Research Data Commons
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.urls import reverse
from horizon import exceptions
from horizon import forms
from horizon import messages


from nectar_dashboard.api import manuka


LOG = logging.getLogger(__name__)

# The known values of the 'affiliation' attribute as defined
# by the AAF
FACULTY = 'faculty'
STUDENT = 'student'
STAFF = 'staff'
EMPLOYEE = 'employee'
MEMBER = 'member'
AFFILIATE = 'affiliate'
ALUM = 'alum'
LIBRARY_WALK_IN = 'library-walk-in'

AFFILIATION_CHOICES = [
    (FACULTY, 'Faculty'),
    (STUDENT, 'Student'),
    (STAFF, 'Staff'),
    (EMPLOYEE, 'Employee'),
    (MEMBER, 'Member'),
    (AFFILIATE, 'Affiliate'),
    (ALUM, 'Alumnus'),
    (LIBRARY_WALK_IN, 'Library walk-in'),
]


class UpdateForm(forms.SelfHandlingForm):
    affiliation = forms.ChoiceField(
        required=True,
        choices=AFFILIATION_CHOICES,
        help_text="Your affiliation to your organisation.",
    )

    orcid = forms.CharField(max_length=64, label="ORCID", required=False)

    phone_number = forms.CharField(max_length=64, required=False)

    mobile_number = forms.CharField(max_length=64, required=False)

    def handle(self, request, data):
        user_id = self.initial['id']
        try:
            client = manuka.manukaclient(self.request)
            user = client.users.update(user_id, **data)
        except Exception:
            redirect = reverse("horizon:settings:my-details:edit-self")
            exceptions.handle(
                request, 'Unable to update user.', redirect=redirect
            )

        message = f'Updating user "{user.email}"'
        messages.info(request, message)
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = (
                'form-control ' + field.widget.attrs.get('class', '')
            )
