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

from rest_framework import serializers

from nectar_dashboard.rcallocation.api import base
from nectar_dashboard.rcallocation import models


class ARDCSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ARDCSupport
        fields = '__all__'


class ARDCSupportViewSet(base.NoDestroyViewSet):
    queryset = models.ARDCSupport.objects.all()
    serializer_class = ARDCSupportSerializer


class NCRISFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NCRISFacility
        fields = '__all__'


class NCRISFacilityViewSet(base.NoDestroyViewSet):
    queryset = models.NCRISFacility.objects.all()
    serializer_class = NCRISFacilitySerializer
