from django.conf.urls import re_path

from nectar_dashboard.usage.allocation_usage import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
]
