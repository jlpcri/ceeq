from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse

from ceeq.apps.queries.models import Project, Instance, ImpactMap
from ceeq.apps.queries.views import projects


class ProjectsViewTest(TestCase):
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
        # self.project = Project.objects.create(
        #     name='Temp Project',
        #     jira_key='TP',
        #     jira_version='1.0',
        #     instance=self.instance,
        #     impact_map=self.impact_map
        # )
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
        self.superuser_accout = {
            'username': 'SuperUser',
            'password': 'SuperPassword'
        }
        self.user_super = User.objects.create_superuser(
            username=self.superuser_accout['username'],
            password=self.superuser_accout['password'],
            email=''
        )

    def test_projects_url_resolve_to_view(self):
        found = resolve(reverse('queries:projects'))
        self.assertEqual(found.func, projects)

    def test_projects_view_with_no_projects(self):
        response = self.client.get(reverse('queries:projects'))
        self.assertContains(response, 'No projects available', status_code=200)