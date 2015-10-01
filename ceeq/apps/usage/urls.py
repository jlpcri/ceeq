from django.conf.urls import patterns, url


urlpatterns = patterns('ceeq.apps.usage.views',
    url(r'^$', 'usage', name='usage'),
    url(r'^project_access/$', 'get_project_access_trend', name='get_project_access_trend'),

)
