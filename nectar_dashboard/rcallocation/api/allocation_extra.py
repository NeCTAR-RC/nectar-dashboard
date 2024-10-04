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
from rest_framework import viewsets

from nectar_dashboard.rcallocation.api import auth
from nectar_dashboard.rcallocation.api import fields
from nectar_dashboard.rcallocation import models
from nectar_dashboard import rest_auth


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
                f"Allocation in status '{allocation.get_status_display()}' "
                "can not be updated"
            )

        return data


class AllocationRelatedViewSet(viewsets.ModelViewSet, auth.PermissionMixin):
    permission_classes = (rest_auth.ApproverOrOwner, rest_auth.CanUpdate)
    filterset_fields = ('allocation',)

    def get_queryset(self):
        if self.is_read_admin():
            return self.queryset
        elif self.request.user.is_authenticated:
            return self.queryset.filter(
                allocation__contact_email=self.request.user.username
            )


class ChiefInvestigatorSerializer(AllocationRelatedSerializer):
    primary_organisation = fields.PrimaryOrganisationField(
        many=False, queryset=models.Organisation.objects.all()
    )

    class Meta:
        model = models.ChiefInvestigator
        fields = '__all__'


class ChiefInvestigatorViewSet(AllocationRelatedViewSet):
    queryset = models.ChiefInvestigator.objects.all()
    serializer_class = ChiefInvestigatorSerializer


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
