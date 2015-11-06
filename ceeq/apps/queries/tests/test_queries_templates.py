from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.urlresolvers import resolve, reverse

from ceeq.apps.queries.models import Project, ImpactMap, Instance
from ceeq.apps.queries.forms import ProjectForm, ProjectNewForm


class ProjectTemplateTest(TestCase):
    def setUp(self):
        self.client = Client()

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
        self.user_account = {
            'username': 'correctName',
            'password': 'correctPassword'
        }
        self.user = User.objects.create_user(
            username=self.user_account['username'],
            password=self.user_account['password']
        )
        self.client.login(
            username=self.user_account['username'],
            password=self.user_account['password']
        )
        self.superuser_account = {
            'username': 'SuperUser',
            'password': 'SuperPassword'
        }
        self.user_super = User.objects.create_superuser(
            username=self.superuser_account['username'],
            password=self.superuser_account['password'],
            email=''
        )

    def test_projects_view_returns_code_200(self):
        response = self.client.get(reverse('queries:projects'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_projects_view_contains_correct_url_to_project_detail(self):

        response = self.client.get(reverse('queries:projects'))
        self.assertContains(response, reverse('queries:project_detail',
                                              kwargs={'project_id': self.project.id}))

    def test_projects_view_contains_url_to_jira_key(self):
        response = self.client.get(reverse('queries:projects'), follow=True)
        self.assertContains(response, self.project.instance.url + '/issues/?jql=project=' + self.project.jira_key)

    def test_projects_view_contains_url_to_jira_version(self):
        response = self.client.get(reverse('queries:projects'), follow=True)
        self.assertContains(response, self.project.instance.url
                            + '/issues/?jql=project='
                            + self.project.jira_key
                            + ' AND affectedVersion = \"'
                            + self.project.jira_version
                            + '\"')

    def test_projects_view_contains_url_to_impactMap_framework(self):
        response = self.client.get(reverse('queries:projects'), follow=True)
        self.assertContains(response, '#framework')

    def test_projects_view_not_contains_url_to_project_new_normaluser(self):
        response = self.client.get(reverse('queries:projects'), follow=True)
        self.assertNotContains(response, '#project-new-modal')

    def test_projects_view_contains_url_to_project_new_superuser(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        response = self.client.get(reverse('queries:projects'), follow=True)
        self.assertContains(response, '#project-new-modal')

    def test_projects_view_not_contains_url_to_query_jira_data_normaluser(self):
        response = self.client.get(reverse('queries:projects'), follow=True)
        self.assertNotContains(response, '/ceeq/queries/query_jira_data_all')

    def test_projects_view_contains_url_to_query_jira_data_superuser(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        response = self.client.get(reverse('queries:projects'), follow=True)
        self.assertContains(response, '/ceeq/queries/query_jira_data_all')

    def test_projects_view_not_contains_url_to_calculate_all_normaluser(self):
        response = self.client.get(reverse('queries:projects'), follow=True)
        self.assertNotContains(response, '/ceeq/calculator')

    def test_projects_view_contains_url_to_calculate_all_superuser(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        response = self.client.get(reverse('queries:projects'), follow=True)
        self.assertContains(response, '/ceeq/calculator')


class ProjectFormTemplatesTest(TestCase):
    def setUp(self):
        self.client = Client()

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
        self.user_account_correct = {
            'username': 'correctName',
            'password': 'correctPassword'
        }
        self.user = User.objects.create_superuser(
            username=self.user_account_correct['username'],
            password=self.user_account_correct['password'],
            email=''
        )
        self.client.login(
            username=self.user_account_correct['username'],
            password=self.user_account_correct['password']
        )

    def test_project_detail_contains_detail_form(self):
        response = self.client.get(reverse('queries:project_detail',
                                           kwargs={'project_id': self.project.id}))

        form = ProjectForm(instance=self.project)
        for field in form:
            self.assertContains(response, field.html_name)

    def test_projects_view_contains_new_form(self):
        response = self.client.get(reverse('queries:projects'))
        form = ProjectNewForm()
        for field in form:
            self.assertContains(response, field.html_name)
