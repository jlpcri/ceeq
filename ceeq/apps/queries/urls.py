from django.conf.urls import patterns, url

urlpatterns = patterns('ceeq.apps.queries.views',
                       url(r'^$', 'projects', name='q_projects'),
                       url(r'^new/$', 'project_new', name='q_project_new'),
                       url(r'^(?P<project_id>\d+)/$', 'project_detail', name='q_project_detail'),
                       url(r'^(?P<project_id>\d+)/archive/$', 'project_archive', name='q_project_archive'),
                       url(r'^(?P<project_id>\d+)/track/$', 'project_track', name='q_project_track'),

                       )
