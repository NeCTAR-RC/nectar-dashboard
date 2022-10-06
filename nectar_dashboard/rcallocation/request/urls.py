from django.conf.urls import url

from nectar_dashboard.rcallocation.request import views


urlpatterns = [
    url(r'^init_organisations/$', views.init_organisations),
    url(r'^fetch_organisations/$', views.fetch_organisations),
    url(r'^$', views.AllocationCreateView.as_view(), name='request'),
]
