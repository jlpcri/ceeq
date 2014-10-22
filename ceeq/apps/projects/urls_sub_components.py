from django.conf.urls import patterns, url


urlpatterns = patterns('ceeq.apps.projects.views_sub_components',
      url(r'^project/(?P<project_id>\d+)/Application/?$', 'project_sub_apps_piechart', name='project_sub_apps_piechart'),
      url(r'^project/(?P<project_id>\d+)/CXP/?$', 'project_sub_cxp_piechart', name='project_sub_cxp_piechart'),
      url(r'^project/(?P<project_id>\d+)/Platform/?$', 'project_sub_platform_piechart', name='project_sub_platform_piechart'),
      url(r'^project/(?P<project_id>\d+)/Reports/?$', 'project_sub_reports_piechart', name='project_sub_reports_piechart'),

      url(r'^project/apps_sub_pie/(?P<project_id>\d+)/?$', 'fetch_apps_subcomponents_pie', name='fetch_apps_subcomponents_pie'),
      url(r'^project/cxp_sub_pie/(?P<project_id>\d+)/?$', 'fetch_cxp_subcomponents_pie', name='fetch_cxp_subcomponents_pie'),
      url(r'^project/platform_sub_pie/(?P<project_id>\d+)?/$', 'fetch_platform_subcomponents_pie', name='fetch_platform_subcomponents_pie'),
      url(r'^project/reports_sub_pie/(?P<project_id>\d+)/?$', 'fetch_reports_subcomponents_pie', name='fetch_reports_subcomponents_pie'),

      )