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


from functools import partial

from django.conf import settings
from django_filters import rest_framework as filters
from rest_framework import decorators
from rest_framework import exceptions
from rest_framework import permissions
from rest_framework import response
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import utils
from nectar_dashboard import rest_auth


try:
    list_route_decorator = partial(decorators.action, detail=False)
    detail_route_decorator = partial(decorators.action, detail=True)
except AttributeError:
    list_route_decorator = decorators.list_route
    detail_route_decorator = decorators.detail_route


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

    def is_write_admin(self):
        if self.request.user.is_authenticated:
            roles = set([role['name'].lower()
                         for role in self.request.user.roles])
            required = set(settings.ALLOCATION_GLOBAL_ADMIN_ROLES
                           + settings.ALLOCATION_APPROVER_ROLES)
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

    @list_route_decorator()
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


class ServiceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (rest_auth.ReadOrAdmin,)
    queryset = models.ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (rest_auth.ReadOrAdmin,)
    queryset = models.Resource.objects.all()
    serializer_class = ResourceSerializer


class SiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Site
        fields = '__all__'


class SiteViewSet(viewsets.ModelViewSet):
    permission_classes = (rest_auth.ReadOrAdmin,)
    queryset = models.Site.objects.all()
    serializer_class = SiteSerializer

    def destroy(self, request, *args, **kwargs):
        # Sites should be disabled, not destroyed.
        return response.Response({'error': 'Sites should not be destroyed'},
                                 status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ApproverSerializer(serializers.ModelSerializer):
    sites = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Site.objects.all())

    class Meta:
        model = models.Approver
        fields = '__all__'


class ApproverViewSet(viewsets.ModelViewSet):
    queryset = models.Approver.objects.all()
    serializer_class = ApproverSerializer

    def destroy(self, request, *args, **kwargs):
        # Approvers should be disabled, not destroyed.
        return response.Response({'error':
                                  'Approvers should not be destroyed'},
                                 status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [rest_auth.IsAdminOrApprover]
        else:
            permission_classes = [rest_auth.IsAdmin]
        return [permission() for permission in permission_classes]


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

        if data['quota'] < -2:
            raise serializers.ValidationError("Quota value invalid")
        if data['requested_quota'] < -2:
            raise serializers.ValidationError("Requested quota value invalid")
        if allocation.managed:
            # Unlimited quota is only allowed for UoM local allocations ...
            if data['quota'] == -1:
                raise serializers.ValidationError(
                    "Unlimited quota not allowed")
            if data['requested_quota'] == -1:
                raise serializers.ValidationError(
                    "Unlimited requested quota not allowed")

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


def valid_site(name):
    if not name:
        return None
    try:
        return models.Site.objects.get(name=name)
    except models.Site.DoesNotExist:
        raise serializers.ValidationError("Site '%s' does not exist" % name)


class AllocationHomeField(serializers.Field):
    def to_representation(self, obj):
        return obj.allocation_home

    def to_internal_value(self, data):
        if data == 'unassigned':
            return {'allocation_home': {'national': False,
                                        'associated_site': None}}
        if data == 'national':
            # Leave the existing 'associated_site' value alone.
            # We don't know what it *should* be.
            return {'allocation_home': {'national': True}}
        site = valid_site(data)
        if site is None:
            raise serializers.ValidationError(
                "'allocation_home' must be a real site name")
        return {'allocation_home': {'national': False,
                                    'associated_site': site}}


class AssociatedSiteField(serializers.Field):
    def to_representation(self, obj):
        return obj.name if obj else None

    def to_internal_value(self, data):
        site = valid_site(data)
        return site


class UsageTypesField(serializers.RelatedField):
    # We must allow creation, etc of an allocation request with
    # no usage types via the API.  Alternatives are impractical.

    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        try:
            usage_type = models.UsageType.objects.get(name=data)
            if not usage_type.enabled:
                raise serializers.ValidationError(
                    "UsageType '%s' is disabled" % data)
            return usage_type
        except models.UsageType.DoesNotExist:
            raise serializers.ValidationError(
                "'%s' is not a known UsageType" % data)


class AllocationSerializer(serializers.ModelSerializer):
    quotas = QuotaGroupsField(many=False, read_only=True)
    status_display = serializers.SerializerMethodField()
    chief_investigator = serializers.SerializerMethodField()
    allocation_home = AllocationHomeField(source='*',
                                          required=False)
    allocation_home_display = serializers.SerializerMethodField()
    associated_site = AssociatedSiteField(allow_null=True,
                                          required=False)
    usage_types = UsageTypesField(many=True,
                                  queryset=models.UsageType.objects.all())

    class Meta:
        model = models.AllocationRequest
        exclude = ('created_by', 'notes', 'status_explanation',
                   'parent_request')
        read_only_fields = ('status', 'start_date', 'end_date',
                            'national', 'associated_site',
                            'contact_email', 'approver_email',
                            'project_id', 'provisioned', 'notifications',
                            'allocation_home',
                            'allocation_home_display', 'managed')

    @staticmethod
    def get_status_display(obj):
        return obj.get_status_display()

    @staticmethod
    def get_allocation_home_display(obj):
        return obj.allocation_home_display

    @staticmethod
    def get_chief_investigator(obj):
        investigators = obj.investigators.all()
        if investigators:
            # Should only be one ci per allocation
            ci = investigators[0]
            return str(ci.email)
        return None

    def validate_project_name(self, value):
        if not utils.is_project_name_available(value):
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
        read_only_fields = ('parent_request', 'approver_email', 'status'),


class AllocationFilter(filters.FilterSet):
    parent_request__isnull = filters.BooleanFilter(name='parent_request',
                                                   lookup_expr='isnull')
    chief_investigator = filters.CharFilter('investigators__email')
    allocation_home = filters.CharFilter(method='filter_allocation_home')
    associated_site = filters.CharFilter('associated_site__name')

    def filter_allocation_home(self, queryset, name, value):
        if value == 'national':
            return queryset.filter(national=True)
        elif value == 'unassigned':
            return queryset.filter(national=False) \
                           .filter(associated_site__isnull=True)
        else:
            return queryset.filter(associated_site__name=value) \
                           .filter(national=False)

    class Meta:
        model = models.AllocationRequest

        fields = {'status': ['exact', 'in'],
                  'parent_request_id': ['exact'],
                  'project_id': ['exact', 'in'],
                  'project_name': ['exact', 'contains', 'icontains',
                                   'startswith', 'istartswith', 'endswith',
                                   'iendswith', 'regex'],
                  'convert_trial_project': ['exact'],
                  'provisioned': ['exact'],
                  'parent_request': ['exact'],
                  'associated_site': ['exact'],
                  'national': ['exact'],
                  'managed': ['exact'],
                  'notifications': ['exact'],
                  'contact_email': ['exact', 'contains', 'icontains',
                                    'startswith', 'istartswith', 'endswith',
                                    'iendswith', 'regex'],
                  'approver_email': ['exact', 'contains', 'icontains',
                                     'startswith', 'istartswith', 'endswith',
                                     'iendswith', 'regex'],
                  'start_date': ['exact', 'lt', 'gt', 'gte', 'lte', 'year'],
                  'end_date': ['exact', 'lt', 'gt', 'gte', 'lte', 'year'],
                  'modified_time': ['exact', 'lt', 'gt', 'gte', 'lte', 'date',
                                    'year'],
                  'submit_date': ['exact', 'lt', 'gt', 'gte', 'lte', 'date',
                                  'year'],
                  'created_by': ['exact']}


class AllocationViewSet(viewsets.ModelViewSet, PermissionMixin):
    queryset = models.AllocationRequest.objects.prefetch_related(
        'quotas', 'quotas__quota_set', 'quotas__zone',
        'quotas__quota_set__resource__service_type',
        'quotas__quota_set__resource', 'investigators', 'associated_site')

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
                'quotas__quota_set__resource', 'investigators',
                'associated_site')

    def _perform_create_or_update(self, serializer, kwargs):
        data = serializer.validated_data
        compat_info = data.get('allocation_home')
        if not self.is_write_admin():
            if data.get('national') \
               or data.get('associated_site') \
               or data.get('allocation_home'):
                raise exceptions.PermissionDenied()
        if compat_info:
            if data.get('associated_site') or data.get('national'):
                raise serializers.ValidationError(
                    "Cannot use 'allocation_home' with 'national' or "
                    + "'associated_site'")
            kwargs.update(compat_info)
            data.pop('allocation_home')
        return serializer.save(**kwargs)

    def perform_create(self, serializer):
        kwargs = {'created_by': self.request.user.token.project['id']}
        if not serializer.validated_data.get('contact_email'):
            kwargs['contact_email'] = self.request.user.username
        allocation = self._perform_create_or_update(serializer, kwargs)
        allocation.send_notifications()

    def perform_update(self, serializer):
        self._perform_create_or_update(serializer, {})

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

    @detail_route_decorator(methods=['post'])
    def approve(self, request, pk=None):
        allocation = self.get_object()
        # There are two ways to deal with this.  'approve' could infer the
        # associated site from the request.user.username ... except that
        # "cores" people don't have a single site.  Or it could just say
        # that the associated site must have already been set explicitly;
        # e.g. via an earlier 'create' or 'amend'.
        if (allocation.associated_site is None):
            return response.Response(
                {'error': "The associated_site attribute must be set "
                 "before approving"},
                status=status.HTTP_400_BAD_REQUEST)
        utils.copy_allocation(allocation)
        allocation.status = models.AllocationRequest.APPROVED
        allocation.provisioned = False
        allocation.approver_email = request.user.username
        allocation.save()
        return response.Response(self.get_serializer_class()(allocation).data)

    @detail_route_decorator(methods=['post'])
    def amend(self, request, pk=None):
        allocation = self.get_object()
        utils.copy_allocation(allocation)
        allocation.status = models.AllocationRequest.UPDATE_PENDING
        allocation.provisioned = False
        allocation.save()
        allocation.send_notifications()
        return response.Response(self.get_serializer_class()(allocation).data)

    @detail_route_decorator(methods=['post'])
    def delete(self, request, pk=None):
        allocation = self.get_object()
        # (Deleting an allocation is idempotent)
        if allocation.status != models.AllocationRequest.DELETED:
            utils.copy_allocation(allocation)
            allocation.status = models.AllocationRequest.DELETED
            allocation.save()
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
