from django.conf.urls import re_path

from nectar_dashboard.dashboard_home.welcome import views


urlpatterns = [
    re_path(r'^$', views.HomeView.as_view(), name='welcome'),
    re_path(r'^feed$', views.get_ardc_news, name='feed'),
]
