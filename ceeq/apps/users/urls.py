from django.conf.urls import url

from ceeq.apps.users import views


urlpatterns = [
    url(r'^home/$', views.home, name='home'),
    url(r'^signin/$', views.sign_in, name='sign_in'),
    url(r'^signout/$', views.sign_out, name='sign_out'),
    url(r'^user_management/$', views.user_management, name='management'),
    url(r'^user_update/(?P<user_id>\d+)/$', views.user_update, name='user_update'),
    url(r'^user_delete/(?P<user_id>\d+)/$', views.user_delete, name='user_delete'),

    url(r'^user_settings/$', views.user_settings, name='user_settings'),
    url(r'^user_settings_update/$', views.user_settings_update, name='user_settings_update'),
]
