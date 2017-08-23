from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = template.Library()

QUOTA_ZONES = dict(
    getattr(settings, 'ALLOCATION_NECTAR_AZ_CHOICES', tuple()) +
    getattr(settings, 'ALLOCATION_VOLUME_AZ_CHOICES', tuple()))


@register.filter
@stringfilter
def quota_zone(value):
    if value in QUOTA_ZONES:
        return QUOTA_ZONES[value]
    return value
