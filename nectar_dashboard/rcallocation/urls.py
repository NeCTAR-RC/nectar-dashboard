from django.conf.urls import include
from django.conf.urls import url


urlpatterns = [
    url(r'^select2/', include('select2.urls')),
]
