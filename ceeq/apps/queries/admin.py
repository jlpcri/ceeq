from django.contrib import admin
from models import Instance, Project, ScoreHistory

for m in [Instance, Project, ScoreHistory]:
    admin.site.register(m)