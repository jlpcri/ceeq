from django.conf.urls import patterns, url


urlpatterns = patterns('ceeq.apps.queries.views_sub_components',
                       url(r'(?P<project_id>\d+)/sub/?$', 'project_sub_piechart', name='project_sub_piechart'),
                       url(r'sub_component_pie/(?P<project_id>\d+)/?$', 'fetch_subcomponents_pie_component', name='fetch_subcomponents_pie_component'),

                       )
