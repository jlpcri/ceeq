from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS

from ceeq.apps.projects.models import Project, ProjectComponentsDefectsDensity, FrameworkParameter


class ProjectResource(ModelResource):
    factors = fields.ToManyField('ceeq.api.api.FactorResource',
                                 attribute=lambda bundle: ProjectComponentsDefectsDensity.objects.filter(project=bundle.obj),
                                 full=False,
                                 null=True
    )

    class Meta:
        queryset = Project.objects.all()
        resource_name = 'project'
        authorization = Authorization()
        fields = ['name', 'url', 'modified']
        allowed_methods = ['get', 'post', 'put', 'delete']


class ComponentsDefectsDensityResource(ModelResource):
    project = fields.ToOneField('ceeq.api.api.ProjectResource',
                                attribute='project',
                                related_name='defectsdensity',
                                full=False,
                                null=False
    )

    class Meta:
        queryset = ProjectComponentsDefectsDensity.objects.all()
        resource_name = 'defectsdensity'
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            'weight': ALL,
            'project': ALL,
        }


class FrameworkParameterResource(ModelResource):
    class Meta:
        queryset = FrameworkParameter.objects.all()
        resource_name = 'argument'
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'put', 'delete']


class SearchAutoCompleteResource(Resource):
    def obj_get(self, bundle, **kwargs):
        project_names = Project.objects.all().values_list('name', flat=True)
        results = []
        for name in project_names:
            results.append(name)

        results.sort()
        return results

    def dehydrate(self, bundle):
        # for jquery autocomplete
        if 'term' in bundle.request.GET:
            term = bundle.request.GET['term']
            filtered_results = []
            for name in bundle.obj:
                if name.startswith(term) or name.lower().startswith(term):
                    filtered_results.append(name)
            return filtered_results
        else:
            return bundle.obj

    class Meta:
        resource_name = 'searchAutoComplete'
        authorization = Authorization()
        allowed_method = ['get']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
