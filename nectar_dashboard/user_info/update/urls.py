from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^edit/(?P<pk>\d+)$',
        views.UserEditView.as_view(),
        name='edit'),
    url(r'^edit$',
        views.UserEditSelfView.as_view(),
        name='edit-self'),
]
