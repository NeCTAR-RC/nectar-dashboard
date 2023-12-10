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
from nectar_dashboard import rest_auth


class ApproverSerializer(serializers.ModelSerializer):
    sites = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Site.objects.all())

    class Meta:
        model = models.Approver
        fields = '__all__'


class ApproverViewSet(base.NoDestroyViewSet):
    queryset = models.Approver.objects.all()
    serializer_class = ApproverSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [rest_auth.IsAdminOrApprover]
        else:
            permission_classes = [rest_auth.IsAdmin]
        return [permission() for permission in permission_classes]
