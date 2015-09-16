from collections import OrderedDict
from django import forms
from django.forms import ModelForm, Select
from models import Project


class ProjectForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'jira_key', 'jira_version', 'active', 'complete', 'impact_map']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_version': forms.Select(attrs={'class': 'form-control'})
        }


class ProjectNewForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'jira_key', 'instance', 'active', 'complete', 'impact_map']
        #exclude = ('created', 'score')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_key': forms.TextInput(attrs={'class': 'form-control'}),
            #'jira_version': forms.Select(attrs={'class': 'form-control'})
        }

