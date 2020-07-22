from django.conf.urls import url
from nectar_dashboard.rcallocation.user_allocations.views import RestrictedAllocationsEditView  # noqa
from nectar_dashboard.rcallocation.user_allocations.views import RestrictedAllocationsDetailsView  # noqa
from nectar_dashboard.rcallocation.user_allocations.views import UserAllocationsListView  # noqa
from nectar_dashboard.rcallocation.user_allocations.forms import UserAllocationRequestAmendForm  # noqa

urlpatterns = [
    url(r'^$',
        UserAllocationsListView.as_view(), name='index'),
    url(r'^view/(?P<pk>\d+)/$', RestrictedAllocationsDetailsView.as_view(),
        name='allocation_view'),
    url(r'^edit_request/(?P<pk>\d+)/$',
        RestrictedAllocationsEditView.as_view(),
        name='edit_request'),
    url(r'^edit_change_request/(?P<pk>\d+)/$',
        RestrictedAllocationsEditView.as_view(
            form_class=UserAllocationRequestAmendForm,
            page_title='Request Allocation Extension',
            template_name='rcallocation/allocationrequest_extend.html'),
        name='edit_change_request'),
]
