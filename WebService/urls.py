from django.conf.urls import patterns, include, url
import service
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include('service.urls')),
)
