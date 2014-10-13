from django.contrib.auth.models import User
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


class ProjectFormTemplatesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_account_normaluser = {
            'username': 'normalUserName',
            'password': 'normalUserPassword'
        }
        self.user_normaluser = User.objects.create_superuser(
            username=self.user_account_normaluser['username'],
            password=self.user_account_normaluser['password'],
            email=''
        )

        self.project = Project.objects.create(
            name='Test Project',
            jira_name='Test JIRA Name',
            jira_version='All Versions',
            score=5
        )

    def test_project_detail_contains_form(self):
        self.client.login(
            username=self.user_account_normaluser['username'],
            password=self.user_account_normaluser['password']
        )
        response = self.client.get(reverse('project_detail',
                                           args=[str(self.project.id)]),
                                   follow=True)
        form = ProjectForm()
        for field in form:
            self.assertContains(response, field.html_name)