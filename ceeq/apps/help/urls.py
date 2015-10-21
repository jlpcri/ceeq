from django.conf.urls import patterns, url

urlpatterns = patterns('ceeq.apps.help.views',
                       url(r'^help/guide/$', 'guide', name='guide'),
                       url(r'^help/faq/$', 'faq', name='faq'),
                       )
