from django.conf.urls import patterns, include, url

from schooldata import urls
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^schooldata/', include(urls)),

    url(r'^admin/', include(admin.site.urls)),
)
