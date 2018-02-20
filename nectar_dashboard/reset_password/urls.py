from django.conf.urls import url

from .views import credentials

urlpatterns = [
    url(r'^$', credentials, name='index',),
]
