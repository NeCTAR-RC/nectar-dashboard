from django.conf.urls import url, patterns
from rcportal.rcallocation.views import (
    AllocationDetailView,
    AllocationHistoryView,
)
from rcportal.rcallocation.allocation.views import (
    AllocationUpdateView,
)

from .views import ApprovedAllocationsListView

urlpatterns = patterns('rcportal.rcallocation.allocation_approved',
    url(r'^$', ApprovedAllocationsListView.as_view(), name='approved_requests'),
    url(r'^view/(?P<pk>\d+)/$', AllocationDetailView.as_view(),
        name='allocation_view'),
    url(r'^view/(?P<pk>\d+)/history$', AllocationHistoryView.as_view(),
        name='allocation_history'),
    url(r'^edit_request/(?P<pk>\d+)/$', AllocationUpdateView.as_view(),
        name='edit_request'),
)
