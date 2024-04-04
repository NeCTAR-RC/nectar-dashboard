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

from django_filters import rest_framework as filters
from rest_framework import decorators
from rest_framework import exceptions
from rest_framework import permissions
from rest_framework import response
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets

from nectar_dashboard.rcallocation.api import auth
from nectar_dashboard.rcallocation.api import fields
from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import urgency
from nectar_dashboard.rcallocation import utils
from nectar_dashboard import rest_auth


class AllocationSerializer(serializers.ModelSerializer):
    quotas = serializers.SerializerMethodField()
    bundle = fields.BundleField(required=False)
    status_display = serializers.SerializerMethodField()
    chief_investigator = serializers.SerializerMethodField()
    allocation_home = fields.AllocationHomeField(source='*', required=False)
    allocation_home_display = serializers.SerializerMethodField()
    associated_site = fields.AssociatedSiteField(
        allow_null=True, required=False)
    usage_types = fields.UsageTypesField(
        many=True, queryset=models.UsageType.objects.all())
    ardc_support = fields.ARDCSupportField(
        many=True, queryset=models.ARDCSupport.objects.all())
    ncris_facilities = fields.NCRISFacilitiesField(
        many=True, queryset=models.NCRISFacility.objects.all())
    supported_organisations = fields.OrganisationField(
        many=True, queryset=models.Organisation.objects.all())

    class Meta:
        model = models.AllocationRequest
        exclude = ('created_by', 'notes', 'status_explanation',
                   'parent_request')
        read_only_fields = ('status', 'start_date', 'end_date',
                            'national', 'associated_site',
                            'contact_email', 'approver_email',
                            'project_id', 'provisioned', 'notifications',
                            'special_approval', 'allocation_home',
                            'allocation_home_display', 'managed')

    @staticmethod
    def get_quotas(obj):
        return obj.quota_list()

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

    def validate_supported_organisations(self, value):
        if len(value) > 1:
            for org in value:
                if org.full_name == models.ORG_ALL_FULL_NAME:
                    raise serializers.ValidationError(
                        "'All Organisations' cannot be used in this context")
            if len(set(value)) != len(value):
                raise serializers.ValidationError("Duplicate organisations")
        return value


class PublicAllocationSerializer(AllocationSerializer):
    class Meta:
        model = models.AllocationRequest
        fields = ('id', 'project_name', 'project_description', 'modified_time',
                  'submit_date', 'start_date', 'end_date', 'bundle',
                  'field_of_research_1', 'field_of_research_2',
                  'field_of_research_3', 'for_percentage_1',
                  'for_percentage_2', 'for_percentage_3',
                  'supported_organisations', 'quotas')
        read_only_fields = fields


class AdminAllocationSerializer(AllocationSerializer):

    class Meta:
        model = models.AllocationRequest
        exclude = ('created_by',)
        read_only_fields = ('parent_request', 'approver_email', 'status'),


class AllocationFilter(filters.FilterSet):
    parent_request__isnull = filters.BooleanFilter(field_name='parent_request',
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


class AllocationViewSet(viewsets.ModelViewSet, auth.PermissionMixin):
    queryset = models.AllocationRequest.objects.prefetch_related(
        'quotas', 'quotas__quota_set', 'quotas__zone',
        'quotas__quota_set__resource__service_type',
        'quotas__quota_set__resource', 'investigators',
        'supported_organisations', 'associated_site',
        'ncris_facilities', 'usage_types', 'ardc_support')

    @property
    def filterset_class(self):
        if self.request.user.is_authenticated:
            return AllocationFilter
        return None

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
                'associated_site', 'ncris_facilities', 'usage_types',
                'ardc_support', 'supported_organisations', 'bundle')

    def _perform_create_or_update(self, serializer, kwargs):
        data = serializer.validated_data
        compat_info = data.get('allocation_home')
        if not self.is_write_admin():
            if data.get('national') \
               or data.get('associated_site') \
               or data.get('special_approval') \
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
        elif self.action == 'approver_info':
            permission_classes.append(rest_auth.IsAdminOrApprover)
        elif self.action in ('list', 'retrieve'):
            permission_classes = []
        return [permission() for permission in permission_classes]

    @decorators.action(methods=['post'], detail=True)
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

    @decorators.action(methods=['post'], detail=True)
    def amend(self, request, pk=None):
        allocation = self.get_object()
        utils.copy_allocation(allocation)
        allocation.status = models.AllocationRequest.UPDATE_PENDING
        allocation.provisioned = False
        allocation.save()
        allocation.send_notifications()
        return response.Response(self.get_serializer_class()(allocation).data)

    @decorators.action(methods=['post'], detail=True)
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

    @decorators.action(methods=['get'], detail=True)
    def approver_info(self, request, pk=None):
        """Get the approver info for this allocation, comprising the
        approval urgency, the inferred expiry state and the list of
        sites that are inferred to be 'concerned' with the allocation.
        If the allocation is not pending, we will return 'N/A' as the
        urgency.  This is all derived info, and the derivation process is
        heuristic and subject to tweaking.
        """
        allocation = self.get_object()
        if allocation.parent_request:
            return response.Response(
                {'error': "The allocation cannot be a history record"},
                status=status.HTTP_400_BAD_REQUEST)
        u, e = urgency.get_urgency_info(allocation)
        if allocation.status not in [
                models.AllocationRequest.NEW,
                models.AllocationRequest.SUBMITTED,
                models.AllocationRequest.UPDATE_PENDING]:
            u = "N/A"
        sites = [s.name for s in allocation.get_interested_sites()]
        return response.Response({'approval_urgency': u, 'expiry_state': e,
                                  'concerned_sites': sites})
