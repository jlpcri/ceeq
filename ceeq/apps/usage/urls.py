from django.conf.urls import url

from ceeq.apps.usage import views


urlpatterns = [
    url(r'^$', views.usage, name='usage'),
    url(r'^project_access/$', views.get_project_access_trend, name='get_project_access_trend'),
    url(r'^project_access_update/$', views.update_project_access_history_manually, name='update_project_access_history_manually'),

]
