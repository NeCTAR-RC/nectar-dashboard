from django.conf.urls import patterns, url

from .views import credentials

urlpatterns = patterns('rcportal.passwords.views',
    url(r'^$', credentials, name='index'),
)
