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


class RCShibbolethRouter(object):
    "Route requests for the user_info model to the rcshib database"

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'user_info':
            return 'rcshib'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'user_info':
            return 'rcshib'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'user_info' or \
           obj2._meta.app_label == 'user_info':
            return False
        return None

    def all0w_migration(self, db, app_label, model_name=None, **hints):
        if db == 'rcshib':
            # The schema for the 'rcshib' database is managed by
            # the rcshibboleth project.  Migrations should be done
            # on the other side.
            return False
        return None
