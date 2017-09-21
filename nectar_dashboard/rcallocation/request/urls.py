from django.conf.urls import url, patterns, include
from .views import AllocationCreateView

from rest_framework import routers

from nectar_dashboard.rcallocation import api

router = routers.DefaultRouter()
router.register(r'zones', api.ZoneViewSet)
router.register(r'service-types', api.ServiceTypeViewSet)
router.register(r'resources', api.ResourceViewSet)


urlpatterns = patterns(
    'nectar_dashboard.rcallocation.request',
    url(r'^$', AllocationCreateView.as_view(), name='request'),
    url(r'^api/', include(router.urls)),
)
