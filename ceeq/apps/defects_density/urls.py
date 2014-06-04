from django.conf.urls import patterns, include, url

urlpatterns = patterns('ceeq.apps.defects_density.views',
    url(r'ddensitys/$', 'dd_all', name='dds'),
    url(r'ddensity/new/$', 'dd_new', name='dd_new'),
    url(r'ddensity/(?P<dd_id>\d+)/$', 'dd_detail', name='dd_detail'),
    url(r'ddensity/(?P<dd_id>\d+)/edit/$', 'dd_edit', name='dd_edit'),
    url(r'ddensity/(?P<dd_id>\d+)/delete/$', 'dd_delete', name='dd_delete'),
)
