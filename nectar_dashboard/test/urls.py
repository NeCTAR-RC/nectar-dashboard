#
#    (c) Copyright 2015 Hewlett-Packard Development Company, L.P.
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

"""
URL patterns for the OpenStack Dashboard.
"""

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import re_path
from django.views import defaults
from oslo_utils import importutils
from rest_framework import routers

import horizon.base
from horizon.browsers import views as browsers_views

from openstack_dashboard.api import rest
from openstack_dashboard.test.jasmine import jasmine
from openstack_dashboard import views

import horizon


router = routers.DefaultRouter()
for name, class_str, base_name in settings.REST_VIEW_SETS:
    klass = importutils.import_class(class_str)
    try:
        router.register(name, klass, basename=base_name)
    except TypeError:
        router.register(name, klass, base_name=base_name)

urlpatterns = [
    re_path(r'^$', views.splash, name='splash'),
    re_path(r'^auth/', include('openstack_auth.urls')),
    re_path(r'^api/', include(rest.urls)),
    re_path(r'^jasmine/(.*?)$', jasmine.dispatcher),
    re_path(r'', horizon.base._wrapped_include(horizon.urls)),
    re_path(
        r'^ngdetails/',
        browsers_views.AngularDetailsView.as_view(),
        name='ngdetails',
    ),
    re_path(r'^rest_api/', include(router.urls)),
]

# Development static app and project media serving using the staticfiles app.
urlpatterns += staticfiles_urlpatterns()

# Convenience function for serving user-uploaded media during
# development. Only active if DEBUG==True and the URL prefix is a local
# path. Production media should NOT be served by Django.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns.append(re_path(r'^500/$', defaults.server_error))
