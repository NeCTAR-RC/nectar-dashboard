from django.urls import re_path

from nectar_dashboard.rcallocation.allocation import views as allocation_views
from nectar_dashboard.rcallocation import views


urlpatterns = [
    re_path(r'^$',
            allocation_views.PendingAllocationsListView.as_view(),
            name='allocation_requests'),
    re_path(r'^view/(?P<pk>\d+)/$',
            views.AllocationDetailView.as_view(),
            name='allocation_view'),
    re_path(r'^view/(?P<pk>\d+)/history$',
            views.AllocationHistoryView.as_view(),
            name='allocation_history'),
    re_path(r'^edit_request/(?P<pk>\d+)/$',
            allocation_views.AllocationUpdateView.as_view(),
            name='edit_request'),
    re_path(r'^approve_request/(?P<pk>\d+)/$',
            allocation_views.AllocationApproveView.as_view(),
            name='approve_request'),
    re_path(r'^reject_request/(?P<pk>\d+)/$',
            allocation_views.AllocationRejectView.as_view(),
            name='reject_request'),
    re_path(r'^approve_change_request/(?P<pk>\d+)/$',
            allocation_views.AllocationApproveView.as_view(),
            name='approve_change_request'),
    re_path(r'^edit_notes/(?P<pk>\d+)/$',
            allocation_views.AllocationNotesEdit.as_view(),
            name='edit_notes'),
]
