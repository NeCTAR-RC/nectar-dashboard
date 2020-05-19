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

import horizon

PERMISSIONS_REQUIRED = (('openstack.roles.allocationadmin',
                         'openstack.roles.operator',
                         'openstack.roles.helpdesk',
                         'openstack.roles.admin'),)


class UserLookupPanel(horizon.Panel):
    name = "User Details"
    slug = 'lookup'
    index_url_name = 'list'
    permissions = PERMISSIONS_REQUIRED
