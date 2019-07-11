from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^view/(?P<pk>\d+)$',
        views.UserView.as_view(),
        name='view'),
    url(r'^edit/(?P<pk>\d+)$',
        views.UserEditView.as_view(),
        name='edit'),
    url(r'^edit$',
        views.UserEditSelfView.as_view(),
        name='edit-self'),
]
