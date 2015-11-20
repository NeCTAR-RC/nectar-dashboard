from rest_framework import serializers, viewsets

from nectar_dashboard.rcallocation.models import AllocationRequest, Quota


class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllocationRequest


class AllocationViewSet(viewsets.ModelViewSet):
    queryset = AllocationRequest.objects.all()
    serializer_class = AllocationSerializer
    filter_fields = ('status',)


class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota


class QuotaViewSet(viewsets.ModelViewSet):
    queryset = Quota.objects.all()
    serializer_class = QuotaSerializer
    filter_fields = ('allocation', 'resource', 'zone')
