from django.conf.urls import patterns, url, include

urlpatterns = patterns('ceeq.apps.queries.views',
                       url(r'^$', 'projects', name='q_projects'),
                       url(r'^new/$', 'project_new', name='q_project_new'),
                       url(r'^(?P<project_id>\d+)/$', 'project_detail', name='q_project_detail'),
                       url(r'^(?P<project_id>\d+)/edit/$', 'project_edit', name='q_project_edit'),
                       url(r'^(?P<project_id>\d+)/delete/$', 'project_delete', name='q_project_delete'),
                       url(r'^(?P<project_id>\d+)/archive/$', 'project_archive', name='q_project_archive'),
                       url(r'^(?P<project_id>\d+)/track/$', 'project_track', name='q_project_track'),
                       url(r'^query_jira_data_all/$', 'query_jira_data_all', name='query_jira_data_all'),

                       url(r'^project/scores/$', 'fetch_projects_score', name='q_fetch_projects_score'),

                       url(r'^', include('ceeq.apps.queries.urls_sub_components')),

                       )
