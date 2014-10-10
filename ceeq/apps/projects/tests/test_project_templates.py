from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse

from ceeq.apps.projects.forms import ProjectForm, ProjectNewForm
from ceeq.apps.projects.models import Project


class ProjectTemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = Project.objects.create(
            name='Test Project',
            jira_name='Test JIRA Name',
            jira_version='All Versions',
            score=5
        )
        self.response = self.client.get(reverse('projects'))

    def test_projects_view_return_status_code_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_projects_view_contains_correct_url_to_project(self):
        self.assertContains(self.response, reverse('project_detail',
                                                   args=[str(self.project.id)]))

    def test_projects_view_contains_correct_url_to_defects_density(self):
        self.assertContains(self.response, reverse('project_defects_density',
                                                   args=[str(self.project.id)]))

    def test_projects_view_contains_correct_url_to_update_score(self):
        self.assertContains(self.response, reverse('project_update_scores',
                                                   args=[str(self.project.id)]))

    def test_projects_view_contains_correct_url_to_update_all_scores(self):
        self.assertContains(self.response, reverse('project_update_scores',
                                                   args=[str(1000000)]))

    def test_projects_view_contains_correct_url_to_log_all_scores(self):
        self.assertContains(self.response, reverse('defects_density_log',
                                                   args=[str(1000000)]))

    def test_projects_view_contains_correct_url_to_jira(self):
        self.assertContains(self.response, 'http://jira.west.com/browse/' + self.project.jira_name)

