# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Openstack, LLC
# Copyright 2012 Nebula, Inc.
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

from openstack_dashboard.api.keystone import keystoneclient


class UserNotFound(Exception):
    pass


class DuplicateUsers(Exception):
    pass


def user_get_by_name(request, name, admin=True):
    manager = keystoneclient(request, admin=admin).users
    users = manager.list(name=name)
    if len(users) == 0:
        raise UserNotFound()
    elif len(users) > 1:
        # Just in case ...
        raise DuplicateUsers(name)
    else:
        return users[0]
