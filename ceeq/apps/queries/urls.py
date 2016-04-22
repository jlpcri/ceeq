from django.conf.urls import url, include

from ceeq.apps.queries import views

urlpatterns = [
   url(r'^$', views.projects, name='projects'),
   url(r'^new/$', views.project_new, name='project_new'),
   url(r'^(?P<project_id>\d+)/$', views.project_detail, name='project_detail'),
   url(r'^(?P<project_id>\d+)/edit/$', views.project_edit, name='project_edit'),
   url(r'^(?P<project_id>\d+)/delete/$', views.project_delete, name='project_delete'),
   # url(r'^(?P<project_id>\d+)/archive/$', 'project_archive', name='project_archive'),
   # url(r'^(?P<project_id>\d+)/track/$', 'project_track', name='project_track'),
   url(r'^query_jira_data_all/$', views.query_jira_data_all, name='query_jira_data_all'),

   url(r'^project/scores/$', views.fetch_projects_score, name='fetch_projects_score'),

   url(r'^', include('ceeq.apps.queries.urls_sub_components')),

]
