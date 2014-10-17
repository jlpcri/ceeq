from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse


from ceeq.apps.projects.models import Project
from ceeq.apps.projects.views_sub_components import project_sub_apps_piechart,\
    project_sub_cxp_piechart, project_sub_platform_piechart, project_sub_reports_piechart


class ProjectSubComponentsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = {
            'name': 'Existing Project',
            'jira_name': 'Existing Jira Name'
        }
        self.project_exist = Project.objects.create(name=self.project['name'],
                                                    jira_name=self.project['jira_name'])

        self.user_account = {
            'username': 'userName',
            'password': 'userPassword',
            'email': ''
        }
        self.user = User.objects.create_user(
            username=self.user_account['username'],
            password=self.user_account['password']
        )
        self.client.login(
            username=self.user_account['username'],
            password=self.user_account['password']
        )

    def test_project_sub_components_apps_url_resolves_to_view(self):
        found = resolve(reverse('project_sub_apps_piechart',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, project_sub_apps_piechart)

    def test_project_sub_components_apps_returns_200(self):
        response = self.client.get(reverse('project_sub_apps_piechart',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to Applications - ' + self.project['name'])

    def test_project_sub_components_cxp_url_resolves_to_view(self):
        found = resolve(reverse('project_sub_cxp_piechart',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, project_sub_cxp_piechart)

    def test_project_sub_components_cxp_returns_200(self):
        response = self.client.get(reverse('project_sub_cxp_piechart',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to CXP - ' + self.project['name'])

    def test_project_sub_components_platform_url_resolves_to_view(self):
        found = resolve(reverse('project_sub_platform_piechart',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, project_sub_platform_piechart)

    def test_project_sub_components_platform_returns_200(self):
        response = self.client.get(reverse('project_sub_platform_piechart',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to Platform - ' + self.project['name'])

    def test_project_sub_components_reports_url_resolves_to_view(self):
        found = resolve(reverse('project_sub_reports_piechart',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, project_sub_reports_piechart)

    def test_project_sub_components_reports_returns_200(self):
        response = self.client.get(reverse('project_sub_reports_piechart',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to Reports - ' + self.project['name'])
