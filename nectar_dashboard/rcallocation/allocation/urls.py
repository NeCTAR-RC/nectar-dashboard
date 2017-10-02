from django.conf.urls import url, patterns

from nectar_dashboard.rcallocation import views
from nectar_dashboard.rcallocation.allocation import views as allocation_views


urlpatterns = patterns('nectar_dashboard.rcallocation.allocation',
    url(r'^$', views.AllocationsListView.as_view(), name='allocation_requests'),
    url(r'^view/(?P<pk>\d+)/$', views.AllocationDetailView.as_view(),
        name='allocation_view'),
    url(r'^view/(?P<pk>\d+)/history$', views.AllocationHistoryView.as_view(),
        name='allocation_history'),
    url(r'^edit_request/(?P<pk>\d+)/$', allocation_views.AllocationUpdateView.as_view(),
        name='edit_request'),
    url(r'^approve_request/(?P<pk>\d+)/$', allocation_views.AllocationApproveView.as_view(),
        name='approve_request'),
    url(r'^reject_request/(?P<pk>\d+)/$', allocation_views.AllocationRejectView.as_view(),
        name='reject_request'),
    url(r'^approve_change_request/(?P<pk>\d+)/$', allocation_views.AllocationApproveView.as_view(),
        name='approve_change_request'),
)
