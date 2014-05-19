from django.conf.urls import patterns, url


urlpatterns = patterns('ceeq.apps.ceeq.views',
      url(r'^projects/$', 'projects', name='projects'),
      url(r'^project/new/$', 'project_new', name='project_new'),
      url(r'^project/(?P<project_id>\d+)/$', 'project_detail', name='project_detail'),
      url(r'^project/(?P<project_id>\d+)/edit/$', 'project_edit', name='project_edit'),
      url(r'^project/(?P<project_id>\d+)/delete/$','project_delete', name='project_delete'),
      url(r'^project/(?P<project_id>\d+)/update_scores/$', 'project_update_scores', name='project_update_scores'),

      url(r'^project/score/$', 'fetch_projects_score', name='fetch_projects_score'),
      #url(r'^characteristics/$', 'characteristics', name='characteristics'),
      )