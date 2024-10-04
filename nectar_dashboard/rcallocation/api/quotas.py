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

from rest_framework import permissions
from rest_framework import response
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets

from nectar_dashboard.rcallocation.api import auth
from nectar_dashboard.rcallocation import models
from nectar_dashboard import rest_auth


class QuotaSerializer(serializers.ModelSerializer):
    zone = serializers.SerializerMethodField()
    allocation = serializers.SerializerMethodField()

    def get_zone(self, obj):
        try:
            return obj.group.zone.name
        except AttributeError:
            return ''

    def get_allocation(self, obj):
        try:
            return obj.group.allocation.id
        except AttributeError:
            return ''

    def validate(self, data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if not user:
            raise serializers.ValidationError("No auth")

        search_args = {'id': self.initial_data['allocation']}
        if not auth.is_write_admin(user):
            search_args['contact_email'] = user.username
        try:
            allocation = models.AllocationRequest.objects.get(**search_args)
        except models.AllocationRequest.DoesNotExist:
            raise serializers.ValidationError("Allocation does not exist")

        if allocation.status not in [
            models.AllocationRequest.SUBMITTED,
            models.AllocationRequest.UPDATE_PENDING,
        ]:
            raise serializers.ValidationError(
                "Allocation quota in status "
                f"'{allocation.get_status_display()}' can not be updated"
            )

        try:
            zone = models.Zone.objects.get(name=self.initial_data['zone'])
        except models.Zone.DoesNotExist:
            raise serializers.ValidationError("Zone does not exist")

        if zone not in data['resource'].service_type.zones.all():
            raise serializers.ValidationError(
                "Resource not available in this zone"
            )

        try:
            group = models.QuotaGroup.objects.get(
                allocation=allocation,
                zone=zone,
                service_type=data['resource'].service_type,
            )
        except models.QuotaGroup.DoesNotExist:
            group = None
        if group:
            try:
                models.Quota.objects.get(
                    resource=data['resource'], group=group
                )
            except models.Quota.DoesNotExist:
                pass
            else:
                raise serializers.ValidationError("Duplicate quota resource")

        if allocation.managed:
            if data['quota'] == -1:
                raise serializers.ValidationError(
                    "Unlimited quota not allowed for managed allocation"
                )
            if data['requested_quota'] == -1:
                raise serializers.ValidationError(
                    "Unlimited requested quota not allowed for managed "
                    "allocation"
                )

        return data

    class Meta:
        model = models.Quota
        exclude = ('group',)


class QuotaViewSet(viewsets.ModelViewSet, auth.PermissionMixin):
    queryset = models.Quota.objects.all()
    serializer_class = QuotaSerializer

    @property
    def filterset_fields(self):
        if self.request.user.is_authenticated:
            return [
                'resource',
                'group__allocation',
                'group__zone',
                'group__service_type',
            ]
        return None

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset
        if self.is_read_admin():
            return self.queryset
        return models.Quota.objects.filter(
            group__allocation__contact_email=self.request.user.username
        )

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        if self.action == 'destroy':
            permission_classes = [rest_auth.CanUpdate]
        elif self.action in ['list', 'retrieve']:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        allocation = models.AllocationRequest.objects.get(
            id=serializer.initial_data['allocation'],
        )
        zone = models.Zone.objects.get(name=serializer.initial_data['zone'])
        st = models.Resource.objects.get(
            id=serializer.initial_data['resource']
        ).service_type
        group, created = models.QuotaGroup.objects.get_or_create(
            allocation=allocation, zone=zone, service_type=st
        )
        serializer.save(group=group)

    def update(self, request, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
