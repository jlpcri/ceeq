from collections import OrderedDict
from django import forms
from django.forms import ModelForm, Select
from models import Project


class ProjectForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'jira_key', 'jira_version', 'instance', 'active', 'complete', 'impact_map']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_key': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_version': forms.Select(attrs={'class': 'form-control'})
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

