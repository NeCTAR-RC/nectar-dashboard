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

from django.db.models import Q

from rest_framework import serializers

from nectar_dashboard.rcallocation import models


def _valid_site(name):
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
        site = _valid_site(data)
        if site is None:
            raise serializers.ValidationError(
                "'allocation_home' must be a real site name")
        return {'allocation_home': {'national': False,
                                    'associated_site': site}}


class AssociatedSiteField(serializers.Field):
    def to_representation(self, obj):
        return obj.name if obj else None

    def to_internal_value(self, data):
        site = _valid_site(data)
        return site


class BundleField(serializers.Field):
    def to_representation(self, obj):
        return obj.name if obj else None

    def to_internal_value(self, data):
        try:
            bundle = models.Bundle.objects.get(name=data)
        except models.Bundle.DoesNotExist:
            raise serializers.ValidationError(
                "Bundle '%s' does not exist" % data)
        else:
            return bundle


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


class OrganisationField(serializers.RelatedField):
    """Serialize as a ROR id (if available) or the native id.
    Deserialization also allows an organisation's short or full name ...
    provided that the name supplied is unambiguous.
    """

    def to_representation(self, value):
        return value.ror_id or value.id

    def to_internal_value(self, data):
        try:
            if data.isdigit():
                organisation = models.Organisation.objects.get(id=int(data))
            else:
                try:
                    organisation = models.Organisation.objects.get(ror_id=data)
                except models.Organisation.DoesNotExist:
                    organisation = models.Organisation.objects.get(
                        Q(full_name__iexact=data)
                        | Q(short_name__iexact=data))
            if not organisation.enabled:
                raise serializers.ValidationError(
                    "Organisation '%s' is disabled" % data)
            return organisation

        except models.Organisation.DoesNotExist:
            raise serializers.ValidationError(
                "'%s' doesn't match a known Organisation" % data)
        except models.Organisation.MultipleObjectsReturned:
            raise serializers.ValidationError(
                "'%s' is an ambiguous Organisation name" % data)


class PrimaryOrganisationField(OrganisationField):
    def to_representation(self, value):
        return value.ror_id or value.id

    def to_internal_value(self, data):
        organisation = super().to_internal_value(data)
        if organisation.full_name == models.ORG_ALL_FULL_NAME:
            raise serializers.ValidationError(
                "'All Organisations' may not be used here")
        return organisation


class NCRISFacilitiesField(serializers.RelatedField):
    def to_representation(self, value):
        return value.short_name

    def to_internal_value(self, data):
        try:
            return models.NCRISFacility.objects.get(
                Q(short_name__iexact=data) | Q(name__iexact=data))
        except models.NCRISFacility.DoesNotExist:
            raise serializers.ValidationError(
                "'%s' is not a known NCRIS Facility" % data)


class ARDCSupportField(serializers.RelatedField):
    def to_representation(self, value):
        return value.short_name

    def to_internal_value(self, data):
        try:
            return models.ARDCSupport.objects.get(
                Q(short_name__iexact=data) | Q(name__iexact=data))
        except models.ARDCSupport.DoesNotExist:
            raise serializers.ValidationError(
                "'%s' is not a known ARDC project or program" % data)
