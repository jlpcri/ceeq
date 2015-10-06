from django.conf.urls import patterns, url, include

urlpatterns = patterns('ceeq.apps.queries.views',
                       url(r'^$', 'projects', name='projects'),
                       url(r'^new/$', 'project_new', name='project_new'),
                       url(r'^(?P<project_id>\d+)/$', 'project_detail', name='project_detail'),
                       url(r'^(?P<project_id>\d+)/edit/$', 'project_edit', name='project_edit'),
                       url(r'^(?P<project_id>\d+)/delete/$', 'project_delete', name='project_delete'),
                       url(r'^(?P<project_id>\d+)/archive/$', 'project_archive', name='project_archive'),
                       url(r'^(?P<project_id>\d+)/track/$', 'project_track', name='project_track'),
                       url(r'^query_jira_data_all/$', 'query_jira_data_all', name='query_jira_data_all'),

                       url(r'^project/scores/$', 'fetch_projects_score', name='fetch_projects_score'),

                       url(r'^', include('ceeq.apps.queries.urls_sub_components')),

                       )
