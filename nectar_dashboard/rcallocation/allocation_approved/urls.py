from django.urls import re_path

from nectar_dashboard.rcallocation.allocation import views as allocation_views
from nectar_dashboard.rcallocation.allocation_approved import views
from nectar_dashboard.rcallocation import views as base_views


urlpatterns = [
    re_path(
        r'^$',
        views.ApprovedAllocationsListView.as_view(),
        name='approved_requests',
    ),
    re_path(
        r'^view/(?P<pk>\d+)/$',
        base_views.AllocationDetailView.as_view(),
        name='allocation_view',
    ),
    re_path(
        r'^view/(?P<pk>\d+)/history$',
        base_views.AllocationHistoryView.as_view(),
        name='allocation_history',
    ),
    re_path(
        r'^edit_request/(?P<pk>\d+)/$',
        allocation_views.AllocationUpdateView.as_view(),
        name='edit_request',
    ),
]
