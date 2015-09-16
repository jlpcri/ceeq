from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from tastypie.api import Api
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from ceeq.api.api import ProjectResource, ComponentsDefectsDensityResource,\
    SearchAutoCompleteResource, FrameworkParameterResource

v1_api = Api(api_name='v1')
v1_api.register(ProjectResource())
v1_api.register(ComponentsDefectsDensityResource())
v1_api.register(SearchAutoCompleteResource())
v1_api.register(FrameworkParameterResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ceeq.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),

    url(r'^ceeq/$', 'ceeq.apps.core.views.landing', name='landing'),
    url(r'^ceeq/', include('ceeq.apps.projects.urls')),
    url(r'^ceeq/', include('ceeq.apps.help.urls')),
    url(r'^ceeq/', include('ceeq.apps.users.urls')),
    url(r'^ceeq/', include('ceeq.apps.search.urls')),
    url(r'^ceeq/', include('ceeq.apps.defects_density.urls')),

    # url(r'^ceeq/', include('ceeq.apps.calculator.urls')),
    # url(r'^ceeq/', include('ceeq.apps.formatter.urls')),
    url(r'^ceeq/queries/', include('ceeq.apps.queries.urls')),

    url(r'^ceeq/admin/', include(admin.site.urls)),
    url(r'^ceeq/api/', include(v1_api.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()