from django.urls import re_path

from nectar_dashboard.usage.trend import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
]
