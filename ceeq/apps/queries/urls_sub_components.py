from django.conf.urls import url

from ceeq.apps.queries import views_sub_components


urlpatterns = [
   url(r'(?P<project_id>\d+)/sub/?$', views_sub_components.project_sub_piechart, name='project_sub_piechart'),
   url(r'sub_component_pie/(?P<project_id>\d+)/?$', views_sub_components.fetch_subcomponents_pie_component, name='fetch_subcomponents_pie_component'),

]
