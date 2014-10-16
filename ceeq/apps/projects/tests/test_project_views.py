from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse


from ceeq.apps.projects.models import Project
from ceeq.apps.projects.views import projects, project_new


class ProjectsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.project1 = {
            'name': 'Test Project 1',
            'jira_name': 'Jira Name 1'
        }
        self.project2 = {
            'name': 'Test Project 2',
            'jira_name': 'Jira Name 2'
        }

    def test_projects_url_resolves_to_view(self):
        found = resolve(reverse('projects'))
        self.assertEqual(found.func, projects)

    def test_projects_view_with_no_projects(self):
        response = self.client.get(reverse('projects'))
        self.assertContains(response, "No projects available", status_code=200)
        self.assertQuerysetEqual(response.context['projects'], [])

    def test_projects_view_contains_projects_list(self):
        p1 = Project(name=self.project1['name'],
                     jira_name=self.project1['jira_name'])
        p1.save()
        p2 = Project(name=self.project2['name'],
                     jira_name=self.project2['jira_name'])
        p2.save()
        response = self.client.get(reverse('projects'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project1['name'])
        self.assertContains(response, self.project1['jira_name'])
        self.assertContains(response, self.project2['name'])
        self.assertContains(response, self.project2['jira_name'])


class ProjectNewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('project_new')
        self.new_project_valid = {
            'name': 'New Project',
            'jira_name': 'New Jira Name',
        }
        self.new_project_without_name = {
            'name': '',
            'jira_name': 'New Jira Name',
        }
        self.new_project_without_jira_name = {
            'name': 'New Project',
            'jira_name': '',
        }
        self.superuser_account_correct = {
            'username': 'correctName',
            'password': 'correctPassword',
            'email': ''
        }
        self.superuser = User.objects.create_superuser(
            username=self.superuser_account_correct['username'],
            password=self.superuser_account_correct['password'],
            email=self.superuser_account_correct['email']
        )
        self.client.login(
            username=self.superuser_account_correct['username'],
            password=self.superuser_account_correct['password']
        )

    def test_project_new_url_resolves_to_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func, project_new)

    def test_project_new_url_returns_status_200(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_project_new_with_valid_data_successful(self):
        response = self.client.post(self.url, self.new_project_valid)
        project = Project.objects.get(name=self.new_project_valid['name'])
        self.assertIsNotNone(project)

    def test_project_new_with_valid_data_redirects_to_projects(self):
        response = self.client.post(self.url, self.new_project_valid)
        project = Project.objects.get(name=self.new_project_valid['name'])
        self.assertRedirects(response, reverse('projects'))

    def test_project_new_without_name_gives_required_error(self):
        response = self.client.post(self.url, self.new_project_without_name)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Correct errors in the form.')

    def test_project_new_without_jira_name_gives_required_error(self):
        response = self.client.post(self.url, self.new_project_without_jira_name)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Correct errors in the form.')