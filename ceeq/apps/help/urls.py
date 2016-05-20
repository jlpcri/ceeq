from django.conf.urls import url

from ceeq.apps.help import views

urlpatterns = [
    url(r'^help/guide/$', views.guide, name='guide'),
    url(r'^help/guide_framework/$', views.guide_framework, name='guide_framework'),
    url(r'^help/faq/$', views.faq, name='faq'),
]
