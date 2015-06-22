from django.contrib import admin

from .models import Project, ProjectComponentsDefectsDensity, FrameworkParameter

model_list = [Project, ProjectComponentsDefectsDensity, FrameworkParameter]

for model in model_list:
    admin.site.register(model)