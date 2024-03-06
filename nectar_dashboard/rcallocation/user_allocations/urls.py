from django.urls import re_path

from nectar_dashboard.rcallocation.user_allocations import forms
from nectar_dashboard.rcallocation.user_allocations import views


urlpatterns = [
    re_path(r'^$',
        views.UserAllocationsListView.as_view(), name='index'),
    re_path(r'^view/(?P<pk>\d+)/$',
            views.RestrictedAllocationsDetailsView.as_view(),
        name='allocation_view'),
    re_path(r'^edit_request/(?P<pk>\d+)/$',
        views.RestrictedAllocationsEditView.as_view(),
        name='edit_request'),
    re_path(r'^edit_change_request/(?P<pk>\d+)/$',
        views.RestrictedAllocationsEditView.as_view(
            form_class=forms.UserAllocationRequestAmendForm,
            page_title='Request Allocation Extension',
            template_name='rcallocation/allocationrequest_extend.html'),
        name='edit_change_request'),
]
