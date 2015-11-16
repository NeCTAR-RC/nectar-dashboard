from django.conf.urls import patterns, url

from .views import credentials

urlpatterns = patterns('nectar_dashboard.reset_password.views',
                       url(r'^$', credentials, name='index',),
)
