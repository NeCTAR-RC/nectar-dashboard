from django.conf.urls import url

from nectar_dashboard.usage.allocation_usage import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
]
