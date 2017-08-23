from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = template.Library()

quota_types = getattr(settings, 'ALLOCATION_QUOTA_TYPES', tuple())


@register.filter
@stringfilter
def quota_title(value):
    if value in quota_types:
        return quota_types[value]
    return value.title().replace('_', ' ')
