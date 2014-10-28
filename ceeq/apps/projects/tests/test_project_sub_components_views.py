from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse


from ceeq.apps.projects.models import Project
from ceeq.apps.projects.views_sub_components import project_sub_piechart


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

    def test_project_sub_components_url_resolves_to_view(self):
        found = resolve(reverse('project_sub_piechart',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, project_sub_piechart)

    def test_project_sub_components_apps_include_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Application',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_apps_exclude_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Application',
            'uat_type': 'exclude_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_apps_only_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Application',
            'uat_type': 'only_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_cxp_include_uat_returns_200(self):
        request_get_data = {
            'component_type': 'CXP',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_cxp_exclude_uat_returns_200(self):
        request_get_data = {
            'component_type': 'CXP',
            'uat_type': 'exclude_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_cxp_only_uat_returns_200(self):
        request_get_data = {
            'component_type': 'CXP',
            'uat_type': 'only_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_platform_include_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Platform',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_platform_exclude_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Platform',
            'uat_type': 'exclude_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_platform_only_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Platform',
            'uat_type': 'only_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_reports_include_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Reports',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_reports_exclude_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Reports',
            'uat_type': 'exclude_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_reports_only_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Reports',
            'uat_type': 'only_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_voiceslots_include_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Voice Slots',
            'uat_type': 'include_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_voiceslots_exclude_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Voice Slots',
            'uat_type': 'exclude_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

    def test_project_sub_components_voiceslots_only_uat_returns_200(self):
        request_get_data = {
            'component_type': 'Voice Slots',
            'uat_type': 'only_uat'
        }
        response = self.client.get(reverse('project_sub_piechart',
                                           args=[self.project_exist.id, ]), request_get_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sub Components Percentage to ' + request_get_data['component_type'] + ' - ' + self.project['name'])
        self.assertContains(response, request_get_data['uat_type'])

