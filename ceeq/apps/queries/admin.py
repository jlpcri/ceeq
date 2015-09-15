from django.contrib import admin
from models import Instance, Project

for m in [Instance, Project]:
    admin.site.register(m)