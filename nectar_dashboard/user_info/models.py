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

import pickle
import re

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models


FACULTY = 'faculty'
STUDENT = 'student'
STAFF = 'staff'
EMPLOYEE = 'employee'
MEMBER = 'member'
AFFILIATE = 'affiliate'
ALUM = 'alum'
LIBRARY_WALK_IN = 'library-walk-in'

AFFILIATION_CHOICES = [(FACULTY, 'Faculty'),
                       (STUDENT, 'Student'),
                       (STAFF, 'Staff'),
                       (EMPLOYEE, 'Employee'),
                       (MEMBER, 'Member'),
                       (AFFILIATE, 'Affiliate'),
                       (ALUM, 'Alumnus'),
                       (LIBRARY_WALK_IN, 'Library walk-in')]

STATE_NEW = 'new'
STATE_REGISTERED = 'registered'
STATE_CREATED = 'created'

STATE_CHOICES = [(STATE_NEW, STATE_NEW),
                 (STATE_REGISTERED, STATE_REGISTERED),
                 (STATE_CREATED, STATE_CREATED)]


def validate_phone(value):
    if not re.compile(r'^(\+[\d]+)?[\d\s]*$').match(value):
        raise ValidationError('Invalid phone number: %(value)s',
                              params={'value': value})


class PhoneField(models.CharField):
    default_validators = [validate_phone]

    def to_python(self, value):
        return value.strip() if value else None


class User(models.Model):
    """Model for user information in the rcshib database

    NB this model is managed by the RCShibboleth project, and the table
    is in the "rcshib" database.  Changes to >>this<< class should track
    changes made in the RCShibboleth project.  Migrations should be
    perfomed on that side too.
    """

    persistent_id = models.CharField(unique=True, max_length=250,
                                     blank=True, null=True)
    user_id = models.CharField(max_length=64, blank=True, null=True)
    displayname = models.CharField(max_length=250, blank=True, null=True)
    email = models.CharField(max_length=250, blank=True, null=True)
    state = models.CharField(max_length=10, blank=True, null=True,
                             choices=STATE_CHOICES,
                             default=STATE_NEW)
    terms_accepted_at = models.DateTimeField(blank=True, null=True)
    shibboleth_attributes = models.BinaryField(blank=True, null=True)
    registered_at = models.DateTimeField(blank=True, null=True)
    terms_version = models.CharField(max_length=64, blank=True, null=True)
    ignore_username_not_email = models.IntegerField(blank=True, null=True)

    first_name = models.CharField(max_length=250, blank=True, null=True)
    surname = models.CharField(max_length=250, blank=True, null=True)
    phone_number = PhoneField(max_length=64, blank=True, null=True)
    mobile_number = PhoneField(max_length=64, blank=True, null=True)
    home_organization = models.CharField(max_length=250, blank=True, null=True)
    orcid = models.CharField(max_length=64, blank=True, null=True)
    affiliation = models.CharField(max_length=64, blank=True, null=True,
                                   choices=AFFILIATION_CHOICES,
                                   default=MEMBER)

    class Meta:
        managed = False
        db_table = 'user'

    def get_absolute_url(self):
        return reverse('horizon:user-info:update:view',
                       args=[self.id])

    @property
    def shibboleth_dict(self):
        return pickle.loads(self.shibboleth_attributes)
