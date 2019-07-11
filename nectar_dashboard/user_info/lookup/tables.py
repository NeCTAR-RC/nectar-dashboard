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

from horizon import tables

LOG = logging.getLogger(__name__)


def user_link(user):
    return user.get_absolute_url()


class UsersTable(tables.DataTable):
    email = tables.Column('email', link=user_link,)
    displayname = tables.Column('displayname', verbose_name='Name')

    user_id = tables.Column('user_id',
                            verbose_name='User ID')

    class Meta:
        name = "registered_users"
        verbose_name = "Registered Nectar Users"
