from django.conf.urls import re_path

from nectar_dashboard.rcallocation.user_allocations.views import RestrictedAllocationsEditView  # noqa
from nectar_dashboard.rcallocation.user_allocations.views import RestrictedAllocationsDetailsView  # noqa
from nectar_dashboard.rcallocation.user_allocations.views import UserAllocationsListView  # noqa
from nectar_dashboard.rcallocation.user_allocations.forms import UserAllocationRequestAmendForm  # noqa

urlpatterns = [
    re_path(r'^$',
        UserAllocationsListView.as_view(), name='index'),
    re_path(r'^view/(?P<pk>\d+)/$', RestrictedAllocationsDetailsView.as_view(),
        name='allocation_view'),
    re_path(r'^edit_request/(?P<pk>\d+)/$',
        RestrictedAllocationsEditView.as_view(),
        name='edit_request'),
    re_path(r'^edit_change_request/(?P<pk>\d+)/$',
        RestrictedAllocationsEditView.as_view(
            form_class=UserAllocationRequestAmendForm,
            page_title='Request Allocation Extension',
            template_name='rcallocation/allocationrequest_extend.html'),
        name='edit_change_request'),
]
