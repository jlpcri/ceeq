from django.conf.urls import patterns, url

urlpatterns = patterns('ceeq.apps.search.views',
   url(r'^search/$', 'search', name='search'),
)