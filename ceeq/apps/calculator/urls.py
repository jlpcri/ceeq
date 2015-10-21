from django.conf.urls import patterns, url

urlpatterns = patterns('ceeq.apps.calculator.views',
                       url(r'^$', 'calculate_score_all', name='calculate_score_all'),)