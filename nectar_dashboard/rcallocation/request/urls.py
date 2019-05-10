from django.conf.urls import url

from nectar_dashboard.rcallocation.request import views


urlpatterns = [
    url(r'^$', views.AllocationCreateView.as_view(), name='request'),
]
