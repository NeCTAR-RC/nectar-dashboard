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

from django.core.urlresolvers import reverse
from django.db import models


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
    state = models.CharField(max_length=10, blank=True, null=True)
    terms_accepted_at = models.DateTimeField(blank=True, null=True)
    shibboleth_attributes = models.BinaryField(blank=True, null=True)
    registered_at = models.DateTimeField(blank=True, null=True)
    terms_version = models.CharField(max_length=64, blank=True, null=True)
    ignore_username_not_email = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'

    def get_absolute_url(self):
        return reverse('horizon:user-info:update:view',
                       args=[self.id])

    @property
    def shibboleth_dict(self):
        return pickle.loads(self.shibboleth_attributes)
