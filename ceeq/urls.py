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

root_path = settings.LOGIN_URL[1:-1]

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ceeq.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),

    url(r'^{0}/$'.format(root_path), 'ceeq.apps.core.views.landing', name='landing'),
    url(r'^{0}/'.format(root_path), include('ceeq.apps.projects.urls')),
    url(r'^{0}/'.format(root_path), include('ceeq.apps.help.urls')),
    url(r'^{0}/'.format(root_path), include('ceeq.apps.users.urls')),
    url(r'^{0}/'.format(root_path), include('ceeq.apps.search.urls')),
    url(r'^{0}/'.format(root_path), include('ceeq.apps.defects_density.urls')),

    url(r'^{0}/admin/'.format(root_path), include(admin.site.urls)),
    url(r'^{0}/api/'.format(root_path), include(v1_api.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()