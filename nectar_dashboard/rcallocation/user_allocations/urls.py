from django.conf.urls import url, patterns
from nectar_dashboard.rcallocation.user_allocations.views import RestrictedAllocationsEditView, RestrictedAllocationsDetailsView, UserAllocationsListView
from nectar_dashboard.rcallocation.user_allocations.forms import UserAllocationRequestAmendForm

urlpatterns = patterns('nectar_dashboard.rcallocation.user_allocations',
    url(r'^$', UserAllocationsListView.as_view(), name='index'),
    url(r'^view/(?P<pk>\d+)/$', RestrictedAllocationsDetailsView.as_view(),
        name='allocation_view'),
    url(r'^edit_request/(?P<pk>\d+)/$', RestrictedAllocationsEditView.as_view(),
        name='edit_request'),
    url(r'^edit_change_request/(?P<pk>\d+)/$',
        RestrictedAllocationsEditView.as_view(
            form_class=UserAllocationRequestAmendForm,
            template_name='rcallocation/allocationrequest_extend.html'),
        name='edit_change_request'),
)
