from django.contrib import admin
from models import ProjectAccess

for m in [ProjectAccess]:
    admin.site.register(m)
