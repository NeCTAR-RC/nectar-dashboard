from django.conf.urls import url, patterns
from views import CramsRedirectView

urlpatterns = patterns('nectar_dashboard.rcallocation.crams',
    url(r'^$', CramsRedirectView.as_view(), name='crams_requests'),
)
