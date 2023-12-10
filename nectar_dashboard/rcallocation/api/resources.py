#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from django.conf import settings
from rest_framework import decorators
from rest_framework import response
from rest_framework import serializers

from nectar_dashboard.rcallocation.api import base
from nectar_dashboard.rcallocation import models


class ZoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Zone
        fields = '__all__'


class ZoneViewSet(base.NoDestroyViewSet):
    queryset = models.Zone.objects.all()
    serializer_class = ZoneSerializer

    @decorators.action(methods=['get'], detail=False)
    def compute_homes(self, request):
        zone_map = settings.ALLOCATION_HOME_ZONE_MAPPINGS
        return response.Response(zone_map)


class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Resource
        fields = '__all__'


class ServiceTypeSerializer(serializers.ModelSerializer):
    resource_set = ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = models.ServiceType
        fields = '__all__'


class ServiceTypeViewSet(base.NoDestroyViewSet):
    queryset = models.ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer


class ResourceViewSet(base.NoDestroyViewSet):
    queryset = models.Resource.objects.all()
    serializer_class = ResourceSerializer


class SiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Site
        fields = '__all__'


class SiteViewSet(base.NoDestroyViewSet):
    queryset = models.Site.objects.all()
    serializer_class = SiteSerializer
