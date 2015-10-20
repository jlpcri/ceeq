from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from tastypie.api import Api
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from ceeq.api.api import SearchAutoCompleteResource, ComponentImpactResource

v1_api = Api(api_name='v1')
v1_api.register(SearchAutoCompleteResource())
v1_api.register(ComponentImpactResource())

urlpatterns = patterns('',

    url(r'^ceeq_new/$', 'ceeq.apps.core.views.landing', name='landing'),
    # url(r'^ceeq_new/', include('ceeq.apps.projects.urls', namespace='projects')),
    url(r'^ceeq_new/', include('ceeq.apps.help.urls', namespace='help')),
    url(r'^ceeq_new/', include('ceeq.apps.users.urls', namespace='users')),
    url(r'^ceeq_new/', include('ceeq.apps.search.urls', namespace='search')),
    # url(r'^ceeq_new/', include('ceeq.apps.defects_density.urls', namespace='dds')),

    url(r'^ceeq_new/calculator/', include('ceeq.apps.calculator.urls', namespace='calculator')),
    # url(r'^ceeq_new/', include('ceeq.apps.formatter.urls', namespace='formatter')),
    url(r'^ceeq_new/queries/', include('ceeq.apps.queries.urls', namespace='queries')),
    url(r'^ceeq_new/usage/', include('ceeq.apps.usage.urls', namespace='usage')),


    url(r'^ceeq_new/admin/', include(admin.site.urls)),
    url(r'^ceeq_new/api/', include(v1_api.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^ceeq_new/__debug__/', include(debug_toolbar.urls)),
    )
