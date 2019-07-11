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

from django.core import urlresolvers
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from horizon import tables

LOG = logging.getLogger(__name__)


def linked_user(user,
                link='horizon:user-info:update:view'):
    url = urlresolvers.reverse(link, args=(user.id,))
    data = mark_safe('<a href="%s">%s</a>' %
                     (escape(url), escape(user.id)))
    return data


class UsersTable(tables.DataTable):
    id = tables.Column(linked_user, verbose_name=_('RCshib id'))
    user_id = tables.Column('user_id',
                            verbose_name=_('Openstack user id'))
    persistent_id = tables.Column('persistent_id',
                                  verbose_name=_('AAF persistent id'))
    email = tables.Column('email', verbose_name=_('AAF email'))

    class Meta:
        name = "registered_users"
        verbose_name = _("Registered Nectar Users")
