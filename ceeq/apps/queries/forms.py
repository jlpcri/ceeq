from collections import OrderedDict
from django import forms
from django.forms import ModelForm, Select
from models import Project


class ProjectForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        if self.instance:
            versions = self.instance.fetch_jira_versions
            choices = tuple(zip(versions, versions))
            self.fields['jira_version'] = forms.ChoiceField(choices=choices,
                                                            widget=forms.Select(attrs={'class': 'form-control'}))
            self.fields['active'] = forms.BooleanField(label='Track Project', required=False)
            self.fields['complete'] = forms.BooleanField(label='Archive Project', required=False)

    class Meta:
        model = Project
        fields = ['name', 'jira_key', 'jira_version', 'instance', 'impact_map', 'active', 'complete', ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_key': forms.TextInput(attrs={'class': 'form-control'}),
            # 'jira_version': forms.Select(attrs={'class': 'form-control'}),
            'instance': forms.Select(attrs={'class': 'form-control'}),
            'impact_map': forms.Select(attrs={'class': 'form-control'})
        }


class ProjectNewForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'jira_key', 'instance', 'impact_map', 'active', 'complete' ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_key': forms.TextInput(attrs={'class': 'form-control'}),
            'instance': forms.Select(attrs={'class': 'form-control'}),
            'impact_map': forms.Select(attrs={'class': 'form-control'})

        }

