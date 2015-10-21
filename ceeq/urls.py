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

root_path = settings.LOGIN_URL[1:-1]

urlpatterns = patterns('',

    url(r'^{0}/$'.format(root_path), 'ceeq.apps.core.views.landing', name='landing'),
    # url(r'^{0}/'.format(root_path), include('ceeq.apps.projects.urls', namespace='projects')),
    url(r'^{0}/'.format(root_path), include('ceeq.apps.help.urls', namespace='help')),
    url(r'^{0}/'.format(root_path), include('ceeq.apps.users.urls', namespace='users')),
    url(r'^{0}/'.format(root_path), include('ceeq.apps.search.urls', namespace='search')),
    # url(r'^{0}/'.format(root_path), include('ceeq.apps.defects_density.urls', namespace='dds')),

    url(r'^{0}/calculator/'.format(root_path), include('ceeq.apps.calculator.urls', namespace='calculator')),
    # url(r'^{0}/'.format(root_path), include('ceeq.apps.formatter.urls', namespace='formatter')),
    url(r'^{0}/queries/'.format(root_path), include('ceeq.apps.queries.urls', namespace='queries')),
    url(r'^{0}/usage/'.format(root_path), include('ceeq.apps.usage.urls', namespace='usage')),


    url(r'^{0}/admin/'.format(root_path), include(admin.site.urls)),
    url(r'^{0}/api/'.format(root_path), include(v1_api.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^{0}/__debug__/'.format(root_path), include(debug_toolbar.urls)),
    )
