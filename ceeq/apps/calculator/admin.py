from django.contrib import admin
from models import ImpactMap, ComponentImpact, SeverityMap, ComponentComplexity, ResultHistory, LiveSettings

for m in [ImpactMap, ComponentImpact, SeverityMap, ComponentComplexity, ResultHistory, LiveSettings]:
    admin.site.register(m)
