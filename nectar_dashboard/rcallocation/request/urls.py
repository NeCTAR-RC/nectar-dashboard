from django.conf.urls import url
from .views import AllocationCreateView


urlpatterns = [
    url(r'^$', AllocationCreateView.as_view(), name='request'),
]
