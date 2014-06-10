from django.forms import ModelForm
from ceeq.apps.projects.models import ProjectComponentsDefectsDensity


class DefectDensityForm(ModelForm):
    class Meta:
        model = ProjectComponentsDefectsDensity
