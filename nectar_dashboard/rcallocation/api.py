from rest_framework import serializers, viewsets
from nectar_dashboard.rcallocation import models


class ZoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Zone
        fields = '__all__'


class ZoneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Zone.objects.all()
    serializer_class = ZoneSerializer


class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Resource
        fields = '__all__'


class ServiceTypeSerializer(serializers.ModelSerializer):
    zones = ZoneSerializer(many=True, read_only=True)
    resource_set = ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = models.ServiceType
        fields = '__all__'


class ServiceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Resource.objects.all()
    serializer_class = ResourceSerializer


class CodeNameField(serializers.RelatedField):
    def to_representation(self, value):
        return value.codename()


class QuotaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Quota
        fields = '__all__'


class InlineQuotaSerializer(serializers.ModelSerializer):
    resource = CodeNameField(read_only=True)

    class Meta:
        model = models.Quota
        fields = ('resource', 'zone', 'quota')


class QuotaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Quota.objects.all()
    serializer_class = QuotaSerializer
    filter_fields = ('allocation', 'resource', 'zone')


class AllocationSerializer(serializers.ModelSerializer):
    quotas = InlineQuotaSerializer(many=True, read_only=True)

    class Meta:
        model = models.AllocationRequest
        fields = '__all__'


class AllocationViewSet(viewsets.ModelViewSet):
    queryset = models.AllocationRequest.objects.all()
    serializer_class = AllocationSerializer
    filter_fields = ('id', 'status', 'parent_request_id', 'project_id',
                     'project_name', 'provisioned')


class ChiefInvestigatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChiefInvestigator
        fields = '__all__'

class ChiefInvestigatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ChiefInvestigator.objects.all()
    serializer_class = ChiefInvestigatorSerializer
    filter_fields = ('allocation',)


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Institution
        fields = '__all__'

class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Institution.objects.all()
    serializer_class = InstitutionSerializer
    filter_fields = ('allocation',)


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Publication
        fields = '__all__'

class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Publication.objects.all()
    serializer_class = PublicationSerializer
    filter_fields = ('allocation',)


class GrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Grant
        fields = '__all__'

class GrantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Grant.objects.all()
    serializer_class = GrantSerializer
    filter_fields = ('allocation',)
