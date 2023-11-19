from django.urls import re_path

from .views import credentials

urlpatterns = [
    re_path(r'^$', credentials, name='index',),
]
