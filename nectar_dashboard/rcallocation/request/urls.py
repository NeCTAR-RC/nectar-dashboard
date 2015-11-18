from django.conf.urls import url, patterns
from .views import AllocationCreateView


urlpatterns = patterns(
    'rcportal.rcallocation.request',
    url(r'^$', AllocationCreateView.as_view(), name='request'),
)
