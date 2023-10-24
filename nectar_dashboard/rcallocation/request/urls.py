from django.conf.urls import re_path

from nectar_dashboard.rcallocation.request import views


urlpatterns = [
    re_path(r'^$', views.AllocationCreateView.as_view(), name='request'),
]
