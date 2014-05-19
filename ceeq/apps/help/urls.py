from django.conf.urls import patterns, url

urlpatterns = patterns('ceeq.apps.help.views',
                       url(r'^help/guide/$', 'help_guide', name='help_guide'),
                       url(r'^help/faq/$', 'help_faq', name='help_faq'),
                       )
