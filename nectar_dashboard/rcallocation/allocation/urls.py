from django.conf.urls import url, patterns
from rcportal.rcallocation.views import (
    AllocationDetailView,
    AllocationsListView,
    AllocationHistoryView,
)
from rcportal.rcallocation.allocation.views import (
    AllocationUpdateView,
    AllocationApproveView,
    AllocationRejectView,
    AllocationProvisionView,
)

urlpatterns = patterns('rcportal.rcallocation.allocation',
    url(r'^$', AllocationsListView.as_view(), name='allocation_requests'),
    url(r'^view/(?P<pk>\d+)/$', AllocationDetailView.as_view(),
        name='allocation_view'),
    url(r'^view/(?P<pk>\d+)/history$', AllocationHistoryView.as_view(),
        name='allocation_history'),
    url(r'^edit_request/(?P<pk>\d+)/$', AllocationUpdateView.as_view(),
        name='edit_request'),
    url(r'^approve_request/(?P<pk>\d+)/$', AllocationApproveView.as_view(),
        name='approve_request'),
    url(r'^reject_request/(?P<pk>\d+)/$', AllocationRejectView.as_view(),
        name='reject_request'),
    url(r'^approve_change_request/(?P<pk>\d+)/$', AllocationApproveView.as_view(),
        name='approve_change_request'),
    url(r'^provision_request/(?P<pk>\d+)/$', AllocationProvisionView.as_view(),
        name='provision_request'),
)
