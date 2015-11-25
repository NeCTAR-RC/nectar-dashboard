from django.conf.urls import url, patterns, include
from .views import AllocationCreateView

from nectar_dashboard.rcallocation import api
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'allocations', api.AllocationViewSet)
router.register(r'quotas', api.QuotaViewSet)


urlpatterns = patterns(
    'nectar_dashboard.rcallocation.request',
    url(r'^$', AllocationCreateView.as_view(), name='request'),
    url(r'^api/', include(router.urls)),
)
