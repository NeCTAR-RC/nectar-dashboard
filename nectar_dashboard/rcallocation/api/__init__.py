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
from django_filters import rest_framework as filters
from rest_framework import decorators
from rest_framework import permissions
from rest_framework import response
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import utils
from nectar_dashboard import rest_auth


class PermissionMixin(object):

    def is_read_admin(self):
        if self.request.user.is_authenticated:
            roles = set([role['name'].lower()
                         for role in self.request.user.roles])
            required = set(settings.ALLOCATION_GLOBAL_ADMIN_ROLES
                           + settings.ALLOCATION_APPROVER_ROLES
                           + settings.ALLOCATION_GLOBAL_READ_ROLES)
            if required & roles:
                return True
        return False


def is_write_admin(user):
    if user.is_authenticated:
        roles = set([role['name'].lower()
                     for role in user.roles])
        required = set(settings.ALLOCATION_GLOBAL_ADMIN_ROLES
                       + settings.ALLOCATION_APPROVER_ROLES)
        if required & roles:
            return True
    return False


class ZoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Zone
        fields = '__all__'


class ZoneViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (rest_auth.ReadOrAdmin,)
    queryset = models.Zone.objects.all()
    serializer_class = ZoneSerializer

    @decorators.list_route()
    def compute_homes(self, request):
        zone_map = {'auckland': ['auckland'],
                    'ersa': ['sa'],
                    'intersect': ['intersect'],
                    'monash': ['monash-01', 'monash-02', 'monash-03'],
                    'nci': ['NCI'],
                    'qcif': ['QRIScloud'],
                    'swinburne': ['swinburne-01'],
                    'tpac': ['tasmania', 'tasmania-s'],
                    'uom': ['melbourne-qh2-uom'],
        }

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


class ServiceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (rest_auth.ReadOrAdmin,)
    queryset = models.ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (rest_auth.ReadOrAdmin,)
    queryset = models.Resource.objects.all()
    serializer_class = ResourceSerializer


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
        if not is_write_admin(user):
            search_args['contact_email'] = user.username
        try:
            allocation = models.AllocationRequest.objects.get(**search_args)
        except models.AllocationRequest.DoesNotExist:
            raise serializers.ValidationError("Allocation does not exist")

        if allocation.status not in [models.AllocationRequest.SUBMITTED,
                                     models.AllocationRequest.UPDATE_PENDING]:
            raise serializers.ValidationError(
                "Allocation quota in status '%s' can not be updated" %
                allocation.get_status_display())

        try:
            zone = models.Zone.objects.get(name=self.initial_data['zone'])
        except models.Zone.DoesNotExist:
            raise serializers.ValidationError("Zone does not exist")

        if zone not in data['resource'].service_type.zones.all():
            raise serializers.ValidationError(
                "Resource not available in this zone")

        try:
            group = models.QuotaGroup.objects.get(
                allocation=allocation, zone=zone,
                service_type=data['resource'].service_type)
        except models.QuotaGroup.DoesNotExist:
            group = None
        if group:
            try:
                models.Quota.objects.get(resource=data['resource'],
                                         group=group)
            except models.Quota.DoesNotExist:
                pass
            else:
                raise serializers.ValidationError("Duplicate quota resource")

        return data

    class Meta:
        model = models.Quota
        exclude = ('group',)


class QuotaGroupsField(serializers.RelatedField):
    def to_representation(self, value):
        quota_groups = value.all()
        output = []
        for quota_group in quota_groups:
            for quota in quota_group.quota_set.all():
                quota_dict = {'zone': quota_group.zone.name,
                              'resource': quota.resource.codename(),
                              'quota': quota.quota,
                              'id': quota.id}
                output.append(quota_dict)
        return output


class QuotaViewSet(viewsets.ModelViewSet, PermissionMixin):
    queryset = models.Quota.objects.all()
    serializer_class = QuotaSerializer
    filter_fields = ('resource', 'group__allocation', 'group__zone',
                     'group__service_type')

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset
        if self.is_read_admin():
            return self.queryset
        return models.Quota.objects.filter(
            group__allocation__contact_email=self.request.user.username)

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
            id=serializer.initial_data['resource']).service_type
        group, created = models.QuotaGroup.objects.get_or_create(
            allocation=allocation,
            zone=zone,
            service_type=st)
        serializer.save(group=group)

    def update(self, request, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class AllocationSerializer(serializers.ModelSerializer):
    quotas = QuotaGroupsField(many=False, read_only=True)
    status_display = serializers.SerializerMethodField()
    chief_investigator = serializers.SerializerMethodField()

    class Meta:
        model = models.AllocationRequest
        exclude = ('created_by', 'notes', 'status_explanation',
                   'allocation_home', 'parent_request')
        read_only_fields = ('status', 'submit_date', 'end_date',
                            'motified_time', 'contact_email', 'approver_email',
                            'project_id', 'provisioned', 'notifications')

    @staticmethod
    def get_status_display(obj):
        return obj.get_status_display()

    @staticmethod
    def get_chief_investigator(obj):
        investigators = obj.investigators.all()
        if investigators:
            # Should only be one ci per allocation
            ci = investigators[0]
            return str(ci.email)
        return None

    def validate_project_name(self, value):
        projects = models.AllocationRequest.objects.filter(project_name=value)
        if projects:
            raise serializers.ValidationError("Project name already exists")
        return value


class PublicAllocationSerializer(AllocationSerializer):
    class Meta:
        model = models.AllocationRequest
        fields = ('id', 'project_name', 'project_description', 'modified_time',
                  'submit_date', 'start_date', 'end_date',
                  'field_of_research_1', 'field_of_research_2',
                  'field_of_research_3', 'for_percentage_1',
                  'for_percentage_2', 'for_percentage_3', 'quotas')
        read_only_fields = fields


class AdminAllocationSerializer(AllocationSerializer):

    class Meta:
        model = models.AllocationRequest
        exclude = ('created_by',)
        read_only_fields = ('parent_request', 'submit_date',
                            'motified_time', 'approver_email',
                            'status', 'end_date'),


class AllocationFilter(filters.FilterSet):
    parent_request__isnull = filters.BooleanFilter(name='parent_request',
                                                   lookup_expr='isnull')
    chief_investigator = filters.CharFilter('investigators__email')

    class Meta:
        model = models.AllocationRequest
        fields = ('status', 'parent_request_id', 'project_id',
                  'project_name', 'provisioned', 'parent_request',
                  'allocation_home', 'contact_email', 'approver_email',
                  'start_date', 'end_date', 'modified_time', 'created_by')


class AllocationViewSet(viewsets.ModelViewSet, PermissionMixin):
    queryset = models.AllocationRequest.objects.prefetch_related(
        'quotas', 'quotas__quota_set', 'quotas__zone',
        'quotas__quota_set__resource__service_type',
        'quotas__quota_set__resource', 'investigators')

    filter_class = AllocationFilter

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset
        if self.is_read_admin():
            return self.queryset
        return models.AllocationRequest.objects.filter(
            contact_email=self.request.user.username).prefetch_related(
                'quotas', 'quotas__quota_set', 'quotas__zone',
                'quotas__quota_set__resource__service_type',
                'quotas__quota_set__resource', 'investigators')

    def perform_create(self, serializer):
        kwargs = {'created_by': self.request.user.token.project['id']}
        if not serializer.validated_data.get('contact_email'):
            kwargs['contact_email'] = self.request.user.username
        serializer.save(**kwargs)

    def get_serializer_class(self):
        if self.is_read_admin():
            return AdminAllocationSerializer
        elif self.request.user.is_authenticated:
            return AllocationSerializer
        else:
            return PublicAllocationSerializer

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]

        if self.action in ['update', 'partial_update']:
            permission_classes.append(rest_auth.CanUpdate)
        elif self.action == 'delete':
            permission_classes.append(rest_auth.CanDelete)
        elif self.action == 'amend':
            permission_classes.append(rest_auth.CanAmend)
        elif self.action == 'approve':
            permission_classes.append(rest_auth.CanApprove)
        elif self.action in ('list', 'retrieve'):
            permission_classes = []
        return [permission() for permission in permission_classes]

    @decorators.detail_route(methods=['post'])
    def approve(self, request, pk=None):
        allocation = self.get_object()
        utils.copy_allocation(allocation)
        allocation.status = models.AllocationRequest.APPROVED
        allocation.provisioned = False
        allocation.approver_email = request.user.username
        allocation.save()
        return response.Response(self.get_serializer_class()(allocation).data)

    @decorators.detail_route(methods=['post'])
    def amend(self, request, pk=None):
        allocation = self.get_object()
        utils.copy_allocation(allocation)
        allocation.status = models.AllocationRequest.UPDATE_PENDING
        allocation.provisioned = False
        allocation.save()
        return response.Response(self.get_serializer_class()(allocation).data)

    @decorators.detail_route(methods=['post'])
    def delete(self, request, pk=None):
        allocation = self.get_object()
        allocation.status = models.AllocationRequest.DELETED
        allocation.save()
        parent_request = allocation.parent_request
        if parent_request:
            parent_request.status = models.AllocationRequest.DELETED
            parent_request.save()
        return response.Response(self.get_serializer_class()(allocation).data)

    def destroy(self, request, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class AllocationRelatedSerializer(serializers.ModelSerializer):

    def validate(self, data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if not user:
            raise serializers.ValidationError("No auth")
        if self.instance:
            allocation_id = self.instance.allocation.id
        else:
            allocation_id = self.initial_data.get('allocation')

        search_args = {'id': allocation_id}
        if not is_write_admin(user):
            search_args['contact_email'] = user.username
        try:
            allocation = models.AllocationRequest.objects.get(**search_args)
        except models.AllocationRequest.DoesNotExist:
            raise serializers.ValidationError("Allocation does not exist")

        if allocation.status not in [models.AllocationRequest.SUBMITTED,
                                     models.AllocationRequest.UPDATE_PENDING]:
            raise serializers.ValidationError(
                "Allocation in status '%s' can not be updated" %
                allocation.get_status_display())

        return data


class AllocationRelatedViewSet(viewsets.ModelViewSet, PermissionMixin):
    permission_classes = (rest_auth.ApproverOrOwner, rest_auth.CanUpdate)
    filter_fields = ('allocation',)

    def get_queryset(self):
        if self.is_read_admin():
            return self.queryset
        elif self.request.user.is_authenticated:
            return self.queryset.filter(
                allocation__contact_email=self.request.user.username)


class ChiefInvestigatorSerializer(AllocationRelatedSerializer):
    class Meta:
        model = models.ChiefInvestigator
        fields = '__all__'


class ChiefInvestigatorViewSet(AllocationRelatedViewSet):
    queryset = models.ChiefInvestigator.objects.all()
    serializer_class = ChiefInvestigatorSerializer


class InstitutionSerializer(AllocationRelatedSerializer):
    class Meta:
        model = models.Institution
        fields = '__all__'


class InstitutionViewSet(AllocationRelatedViewSet):
    queryset = models.Institution.objects.all()
    serializer_class = InstitutionSerializer


class PublicationSerializer(AllocationRelatedSerializer):
    class Meta:
        model = models.Publication
        fields = '__all__'


class PublicationViewSet(AllocationRelatedViewSet):
    queryset = models.Publication.objects.all()
    serializer_class = PublicationSerializer


class GrantSerializer(AllocationRelatedSerializer):
    class Meta:
        model = models.Grant
        fields = '__all__'


class GrantViewSet(AllocationRelatedViewSet):
    queryset = models.Grant.objects.all()
    serializer_class = GrantSerializer
