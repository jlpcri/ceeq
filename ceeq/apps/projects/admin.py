from django.contrib import admin
from django.db.models import get_models, get_app


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'jira_name', 'score')


class ProjectComponentsDefectsDensityAdmin(admin.ModelAdmin):
    list_display = ('project', 'version', 'ceeq')


class FrameworkParameterAdmin(admin.ModelAdmin):
    list_display = ('parameter', 'value')

for model in get_models(get_app('projects')):
    model_admin = locals().get(model.__name__ + 'Admin')
    admin.site.register(model, model_admin)