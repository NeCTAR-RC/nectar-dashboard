from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.UserLookupView.as_view(), name='lookup'),
    url(r'^view/(?P<pk>\d+)$',
        views.UserDetailView.as_view(),
        name='view'),
    url(r'^list/(?P<email>[a-zA-Z0-9.-_@]+)$',
        views.UserListView.as_view(),
        name='list'),
]
