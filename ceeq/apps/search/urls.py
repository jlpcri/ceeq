from django.conf.urls import url

from ceeq.apps.search import views

urlpatterns = [
   url(r'^search/$', views.search, name='search'),
]