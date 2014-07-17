from django.conf.urls import patterns, url, include
from service import views

urlpatterns = patterns('',
    url(r'^kafici/$', views.ListaKafica.as_view()),
    url(r'^kafici/(?P<pk>[0-9]+)/$', views.KaficDetalji.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
)
