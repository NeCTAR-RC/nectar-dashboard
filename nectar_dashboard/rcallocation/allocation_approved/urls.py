from django.conf.urls import url

from nectar_dashboard.rcallocation.allocation import views as allocation_views
from nectar_dashboard.rcallocation.allocation_approved import views
from nectar_dashboard.rcallocation import views as base_views


urlpatterns = [
    url(r'^$', views.ApprovedAllocationsListView.as_view(),
        name='approved_requests'),
    url(r'^view/(?P<pk>\d+)/$', base_views.AllocationDetailView.as_view(),
        name='allocation_view'),
    url(r'^view/(?P<pk>\d+)/history$',
        base_views.AllocationHistoryView.as_view(),
        name='allocation_history'),
    url(r'^edit_request/(?P<pk>\d+)/$',
        views.AllocationUpdateView.as_view(),
        name='edit_request'),
]
