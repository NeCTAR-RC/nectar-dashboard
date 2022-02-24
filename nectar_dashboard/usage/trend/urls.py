from django.conf.urls import url

from nectar_dashboard.usage.trend import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
]
