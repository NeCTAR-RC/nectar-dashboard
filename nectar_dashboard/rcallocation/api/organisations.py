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

from django.core import validators
from django_countries.serializers import CountryFieldMixin
from django_filters import rest_framework as filters
from rest_framework import decorators
from rest_framework import exceptions
from rest_framework import permissions
from rest_framework import response
from rest_framework import serializers

from nectar_dashboard.rcallocation.api import auth
from nectar_dashboard.rcallocation.api import base
from nectar_dashboard.rcallocation import models
from nectar_dashboard import rest_auth


class AdminOrganisationSerializer(CountryFieldMixin,
                                  serializers.ModelSerializer):
    precedes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Organisation.objects.all())

    class Meta:
        model = models.Organisation
        fields = '__all__'


class OrganisationSerializer(CountryFieldMixin, serializers.ModelSerializer):
    precedes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Organisation.objects.all())

    class Meta:
        model = models.Organisation
        exclude = ['vetted_by', 'proposed_by']


class ProposedOrganisationSerializer(CountryFieldMixin,
                                     serializers.ModelSerializer):
    precedes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Organisation.objects.all())
    short_name = serializers.CharField(
        required=True, allow_blank=False, max_length=16)
    url = serializers.CharField(
        required=True, allow_blank=False, max_length=64,
        validators=[validators.URLValidator(schemes=['http', 'https'])])

    class Meta:
        model = models.Organisation
        read_only_fields = ['precedes', 'parent', 'ror_id', 'enabled']
        exclude = ['vetted_by', 'proposed_by']


class OrganisationFilter(filters.FilterSet):

    class Meta:
        model = models.Organisation
        fields = {'ror_id': ['exact', 'iexact'],
                  'short_name': ['exact', 'iexact'],
                  'full_name': ['exact', 'iexact', 'icontains'],
                  'country': ['exact', 'iexact'],
                  'url': ['exact', 'iexact'],
        }


class OrganisationViewSet(base.NoDestroyViewSet, auth.PermissionMixin):
    queryset = models.Organisation.objects.all()
    serializer_class = OrganisationSerializer
    filter_class = OrganisationFilter

    def get_serializer_class(self):
        if self.is_read_admin():
            return AdminOrganisationSerializer
        elif self.action == 'create':
            return ProposedOrganisationSerializer
        else:
            return OrganisationSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        elif self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [rest_auth.IsAdmin]
        return [permission() for permission in permission_classes]

    @decorators.action(methods=['post'], detail=True)
    def approve(self, request, pk=None):
        return self._vet(request, pk=pk, enable=True)

    @decorators.action(methods=['post'], detail=True)
    def decline(self, request, pk=None):
        return self._vet(request, pk=pk, enable=False)

    def _vet(self, request, pk=None, enable=True):
        organisation = self.get_object()
        if organisation.ror_id:
            raise serializers.ValidationError({
                'ror_id': [
                    "An Organisation from the ROR should not be vetted."
                ]})
        try:
            approver = models.Approver.objects.get(
                username=request.user.username)
        except models.Approver.DoesNotExist:
            approver = models.Approver.objects.get(username='system')
        organisation.vetted_by = approver
        organisation.enabled = enable
        organisation.save()
        return response.Response(
            AdminOrganisationSerializer(organisation).data)

    def _check_unique_proposal(self, serializer):
        data = serializer.validated_data
        full_name = data.get('full_name', None)
        if full_name:
            existing = models.Organisation.objects \
                            .filter(full_name__iexact=full_name) \
                            .first()
            if existing:
                raise serializers.ValidationError({
                    'full_name': [
                        "An Organisation with this full name already exists."
                        if existing.enabled
                        else "An Organisation with this full name has "
                        "already been rejected."
                    ]})
        url = data.get('url', None)
        if url:
            existing = models.Organisation.objects \
                            .filter(url__iexact=url) \
                            .first()
            if existing:
                raise exceptions.ValidationError({
                    'url': [
                        "An Organisation with this url already exists."
                        if existing.enabled
                        else "An Organisation with this url has "
                        "already been rejected."
                    ]})

    def perform_create(self, serializer):
        if self.is_write_admin():
            if serializer.validated_data.get('ror_id', '') \
               or serializer.validated_data.get('vetted_by', None) \
               or serializer.validated_data.get('proposed_by', ''):
                # This is assumed to be a classic 'create' since the
                # "propose organization" form doesn't supply any of
                # these fields.
                return serializer.save()

            # Otherwise, this is a propose + vet, so we want to fill
            # in the proposer + vetter + enable
            try:
                approver = models.Approver.objects.get(
                    username=self.request.user.username)
            except models.Approver.DoesNotExist:
                approver = models.Approver.objects.get(username='system')
            kwargs = {'vetted_by': approver,
                      'proposed_by': self.request.user.keystone_user_id,
                      'enabled': True}
        else:
            # This is a proposal that will require vetting
            kwargs = {'vetted_by': None,
                      'proposed_by': self.request.user.keystone_user_id,
                      'enabled': True}
        self._check_unique_proposal(serializer)
        return serializer.save(**kwargs)
