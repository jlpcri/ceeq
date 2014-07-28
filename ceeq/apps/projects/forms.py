from collections import OrderedDict
from django import forms
from django.forms import ModelForm, Select
from models import Project


class ProjectForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        version_names = []
        for item in self.instance.fetch_jira_data['issues']:
            try:
                name = str(item['fields']['versions'][0]['name'])
                version_names.append(name)
            except IndexError:
                continue
        version_names = sorted(list(OrderedDict.fromkeys(version_names)))
        choices = [('All Versions', 'All Versions')]
        choices += [(item, item) for item in version_names]
        #print choices
        self.fields['jira_version'].widget.choices = choices

    class Meta:
        model = Project
        fields = ['name', 'jira_name', 'jira_version', 'active', 'complete']
        #exclude = ('created', 'score')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_version': forms.Select(attrs={'class': 'form-control'})
        }

