from rest_framework import serializers, viewsets

from nectar_dashboard.rcallocation import models


class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AllocationRequest


class AllocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.AllocationRequest.objects.all()
    serializer_class = AllocationSerializer
    filter_fields = ('status', 'parent_request_id', 'tenant_uuid',
                     'tenant_name')


class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Quota


class QuotaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Quota.objects.all()
    serializer_class = QuotaSerializer
    filter_fields = ('allocation', 'resource', 'zone')


class ChiefInvestigatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChiefInvestigator


class ChiefInvestigatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ChiefInvestigator.objects.all()
    serializer_class = ChiefInvestigatorSerializer
    filter_fields = ('allocation',)


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Institution


class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Institution.objects.all()
    serializer_class = InstitutionSerializer
    filter_fields = ('allocation',)


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Publication


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Publication.objects.all()
    serializer_class = PublicationSerializer
    filter_fields = ('allocation',)


class GrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Grant


class GrantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Grant.objects.all()
    serializer_class = GrantSerializer
    filter_fields = ('allocation',)
