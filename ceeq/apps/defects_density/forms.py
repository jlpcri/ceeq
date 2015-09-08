from django.forms import ModelForm
from ceeq.apps.projects.models import ProjectComponentsDefectsDensity


class DefectDensityForm(ModelForm):
    class Meta:
        model = ProjectComponentsDefectsDensity
        fields = ['project', 'version', 'ceeq', 'ceeq_closed', 'cxp', 'platform', 'reports', 'application', 'voice_slots']
