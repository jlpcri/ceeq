from django.conf.urls import url

from ceeq.apps.help import views

urlpatterns = [
    url(r'^help/guide/$', views.guide, name='guide'),
    url(r'^help/faq/$', views.faq, name='faq'),
]
