from django.urls import re_path

from nectar_dashboard.reset_password.views import credentials

urlpatterns = [
    re_path(
        r'^$',
        credentials,
        name='index',
    ),
]
