from django.contrib import admin
from models import Project, ProjectComponentsDefectsDensity, FrameworkParameter


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'jira_name', 'score')


class ProjectComponentsDefectsDensityAdmin(admin.ModelAdmin):
    list_display = ('project', 'version', 'ceeq')


class FrameworkParameterAdmin(admin.ModelAdmin):
    list_display = ('parameter', 'value')

admin.site.register([Project, ProjectComponentsDefectsDensity, FrameworkParameter])
