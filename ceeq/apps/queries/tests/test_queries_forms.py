from django.test import TestCase

from ceeq.apps.queries.forms import ProjectForm, ProjectNewForm
from ceeq.apps.queries.models import Project, Instance, ImpactMap


class ProjectFormTest(TestCase):
    def setUp(self):
        self.instance = Instance.objects.create(
            url='http://jira.west.com',
            jira_user='readonly_sliu_api_user',
            password='qualityengineering',
            jira_fields=['components', 'status', 'priority', 'versions', 'issuetype']
        )
        self.impact_map = ImpactMap.objects.create(
            name='Apps'
        )
        self.project = Project.objects.create(
            name='Temp Project',
            jira_key='TP',
            jira_version='1.0',
            instance=self.instance,
            impact_map=self.impact_map
        )
        self.project_2 = Project.objects.create(
            name='Another Project',
            jira_key='TP',
            jira_version='1.1',
            instance=self.instance,
            impact_map=self.impact_map
        )

    def test_project_form_init_without_instance(self):
        with self.assertRaises(Instance.DoesNotExist):
            ProjectForm()

    def test_project_form_valid_with_valid_params(self):
        data = {
            'name': 'Edit Project Name',
            'jira_key': 'Edit Jira Key',
            'jira_version': 'All Versions',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
            'component_field': Project.COMPONENT,
            'query_field': Project.QUERY_VERSION,
            'active': True,
            'complete': False
        }
        form = ProjectForm(instance=self.project, data=data)
        self.assertTrue(form.is_valid())
        project = form.save()
        self.assertEqual(project.name, data['name'])
        self.assertEqual(project.jira_key, data['jira_key'])
        self.assertEqual(project.jira_version, data['jira_version'])
        self.assertEqual(project.instance, self.instance)
        self.assertEqual(project.impact_map, self.impact_map)

    def test_project_form_invalid_with_blank_data(self):
        form = ProjectForm({}, instance=self.project)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['This field is required.'],
            'jira_key': ['This field is required.'],
            'jira_version': ['This field is required.'],
            'instance': ['This field is required.'],
            'impact_map': ['This field is required.'],
            'component_field': ['This field is required.'],
            'query_field': ['This field is required.']
        })

    def test_project_form_invalid_with_duplicate_name(self):
        data = {
            'name': 'Temp Project',
            'jira_key': 'Edit Jira Key',
            'jira_version': 'All Versions',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
            'active': True,
            'complete': False
        }
        form = ProjectForm(instance=self.project_2, data=data)
        with self.assertRaises(ValueError):
            form.save()


class ProjectNewFormTest(TestCase):
    def setUp(self):
        self.instance = Instance.objects.create(
            url='http://jira.west.com',
            jira_user='readonly_sliu_api_user',
            password='qualityengineering',
            jira_fields=['components', 'status', 'priority', 'versions', 'issuetype']
        )
        self.impact_map = ImpactMap.objects.create(
            name='Apps'
        )
        self.project = Project.objects.create(
            name='Temp Project',
            jira_key='TP',
            jira_version='1.0',
            instance=self.instance,
            impact_map=self.impact_map
        )

    def test_project_new_form_valid_with_valid_params(self):
        data = {
            'name': 'New Project',
            'jira_key': 'Jira Key',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
            'component_field': Project.COMPONENT,
            'query_field': Project.QUERY_VERSION
        }
        form = ProjectNewForm(data=data)
        self.assertTrue(form.is_valid())

    def test_project_new_form_invalid_with_blank_data(self):
        form = ProjectNewForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['This field is required.'],
            'jira_key': ['This field is required.'],
            'instance': ['This field is required.'],
            'impact_map': ['This field is required.'],
            'component_field': ['This field is required.'],
            'query_field': ['This field is required.']
        })

    def test_project_new_form_invalid_with_duplicate_name(self):
        data = {
            'name': 'Temp Project',
            'jira_key': 'TP',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
            'component_field': Project.COMPONENT,
            'query_field': Project.QUERY_VERSION
        }
        form = ProjectNewForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['Project with this Name already exists.']
        })