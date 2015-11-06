from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, resolve

from ceeq.apps.queries.models import Project, ImpactMap, Instance
from ceeq.apps.queries.views_sub_components import project_sub_piechart


class ProjectSubComponentsTest(TestCase):
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

    def test_project_sub_components_url_resolve_to_view(self):
        found = resolve(reverse('queries:project_sub_piechart', args=[self.project.id, ]))
        self.assertEqual(found.func, project_sub_piechart)

    def test_project_sub_components_overall_apps(self):
        request_get_data = {
            'component_type': 'Application',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('queries:project_sub_piechart', args=[self.project.id, ]),
                                   request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project.name)

    def test_project_sub_components_overall_client(self):
        request_get_data = {
            'component_type': 'Client',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('queries:project_sub_piechart', args=[self.project.id, ]),
                                   request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project.name)

    def test_project_sub_components_overall_CXP(self):
        request_get_data = {
            'component_type': 'CXP',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('queries:project_sub_piechart', args=[self.project.id, ]),
                                   request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project.name)

    def test_project_sub_components_overall_Platform(self):
        request_get_data = {
            'component_type': 'Platform',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('queries:project_sub_piechart', args=[self.project.id, ]),
                                   request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project.name)

    def test_project_sub_components_overall_reports(self):
        request_get_data = {
            'component_type': 'Reports',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('queries:project_sub_piechart', args=[self.project.id, ]),
                                   request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project.name)

    def test_project_sub_components_overall_voice(self):
        request_get_data = {
            'component_type': 'Voice',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('queries:project_sub_piechart', args=[self.project.id, ]),
                                   request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project.name)
