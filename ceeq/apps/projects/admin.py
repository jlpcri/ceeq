from django.contrib import admin
from models import Project, ProjectComponentsDefectsDensity, FrameworkParameter, ProjectComponent, ProjectType


model_list = [Project, ProjectType, ProjectComponent, ProjectComponentsDefectsDensity, FrameworkParameter]

for m in model_list:
    admin.site.register(m)

