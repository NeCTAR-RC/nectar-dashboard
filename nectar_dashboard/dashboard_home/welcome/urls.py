from django.conf.urls import url

from nectar_dashboard.dashboard_home.welcome import views


urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='welcome'),
    url(r'^feed$', views.get_ardc_news, name='feed'),
]
