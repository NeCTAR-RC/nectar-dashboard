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


from nectar_dashboard.api.manuka import manukaclient
from nectarclient_lib import exceptions


class UserNotFound(Exception):
    pass


class DuplicateUsers(Exception):
    pass


def user_get_by_name(request, name):
    client = manukaclient(request)
    try:
        user = client.keystone_ext.get_user_by_name(name)
    except exceptions.NotFound:
        raise UserNotFound()
    except exceptions.Conflict:
        # Just in case ...
        raise DuplicateUsers(name)
    else:
        return user
