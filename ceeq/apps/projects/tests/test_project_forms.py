from django.test import TestCase

from ceeq.apps.projects.forms import Project, ProjectForm, ProjectNewForm


class ProjectFormTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name='Test Project',
            jira_name='Test JIRA Name',
            jira_version='All Versions'
        )

    def test_projectform_valid_with_valid_parameters(self):
        data = {
            'name': 'New Test Project',
            'jira_name': self.project.jira_name,
            'jira_version': self.project.jira_version,
        }
        form = ProjectForm(data=data)
        self.assertTrue(form.is_valid())

    def test_projectform_invalid_without_name(self):
        data = {
            'name': None,
            'jira_name': self.project.jira_name,
            'jira_version': self.project.jira_version,
        }
        form = ProjectForm(data=data)
        self.assertFalse(form.is_valid())

    def test_projectform_invalid_with_duplicate_name(self):
        data = {
            'name': 'Test Project',
            'jira_name': self.project.jira_name,
            'jira_version': self.project.jira_version,
        }
        form = ProjectForm(data=data)
        self.assertFalse(form.is_valid())

    def test_projectform_invalid_without_jira_name(self):
        data = {
            'name': 'Test Project',
            'jira_name': None,
            'jira_version': self.project.jira_version,
        }
        form = ProjectForm(data=data)
        self.assertFalse(form.is_valid())

    def test_projectform_invalid_with_invalid_jira_version(self):
        data = {
            'name': 'Test Project',
            'jira_name': self.project.jira_name,
            'jira_version': None,
        }
        form = ProjectForm(data=data)
        self.assertFalse(form.is_valid())


class ProjectNewFormTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name='Test Project',
            jira_name='Test JIRA Name',
            jira_version='All Versions'
        )
        self.new_project_data = {
            'name': 'New Project',
            'jira_name': 'New Project Jira Name'
        }
        self.new_project_data_no_name = {
            'name': None,
            'jira_name': 'New Project Jira Name'
        }
        self.new_project_data_no_jira_name = {
            'name': 'New Project',
            'jira_name': None
        }

    def test_projectnewform_valid_with_valid_parameters(self):
        form = ProjectNewForm(data=self.new_project_data)
        self.assertTrue(form.is_valid())

    def test_projectnewform_invalid_with_no_name(self):
        form = ProjectNewForm(data=self.new_project_data_no_name)
        self.assertFalse(form.is_valid())

    def test_projectnewform_invalid_with_no_jira_name(self):
        form = ProjectNewForm(data=self.new_project_data_no_jira_name)
        self.assertFalse(form.is_valid())

    def test_projectnewform_invalid_with_duplicate_name(self):
        data = {
            'name': self.project.name,
            'jira_name': self.project.jira_name
        }
        form = ProjectNewForm(data=data)
        self.assertFalse(form.is_valid())