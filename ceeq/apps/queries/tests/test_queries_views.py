from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse

from ceeq.apps.queries.models import Project, Instance, ImpactMap
from ceeq.apps.queries.views import projects, project_new, project_detail, project_edit, project_delete


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

    def test_projects_url_resolve_to_view(self):
        found = resolve(reverse('queries:projects'))
        self.assertEqual(found.func, projects)

    def test_projects_view_with_no_projects(self):
        response = self.client.get(reverse('queries:projects'))
        self.assertContains(response, 'No projects available', status_code=200)
        self.assertQuerysetEqual(response.context['projects_active'], [])
        self.assertQuerysetEqual(response.context['projects_archive'], [])

    def test_projects_view_contains_projects_list(self):
        p1 = Project.objects.create(
            name='First Project',
            jira_key='key1',
            jira_version='first project version',
            instance=self.instance,
            impact_map=self.impact_map
        )
        p2 = Project.objects.create(
            name='Second Project',
            jira_key='key2',
            jira_version='second project version',
            instance=self.instance,
            impact_map=self.impact_map,
            complete=True
        )
        response = self.client.get(reverse('queries:projects'))
        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(response.context['projects_active'],
                                 ['<Project: First Project: key1: first project version>'])
        self.assertContains(response, p1.name)
        self.assertContains(response, p1.jira_key)
        self.assertContains(response, p1.jira_version)
        self.assertContains(response, p1.internal_score)
        self.assertContains(response, p1.impact_map.name)
        self.assertContains(response, p1.instance.url)

        self.assertQuerysetEqual(response.context['projects_archive'],
                                 ['<Project: Second Project: key2: second project version>'])
        self.assertContains(response, p2.name)
        self.assertContains(response, p2.jira_key)
        self.assertContains(response, p2.jira_version)
        self.assertContains(response, p2.internal_score)
        self.assertContains(response, p2.impact_map.name)
        self.assertContains(response, p2.instance.url)

    def test_projects_view_contains_other_2_tabs(self):
        p1 = Project.objects.create(
            name='First Project',
            jira_key='key1',
            jira_version='first project version',
            instance=self.instance,
            impact_map=self.impact_map
        )

        response = self.client.get(reverse('queries:projects'))
        self.assertContains(response, '<a href="#score_overall" data-toggle="tab">CEEQ Score</a>')
        self.assertContains(response, '<div class="tab-pane" id="score_overall">')
        self.assertContains(response, '<a href="#framework_parameter" data-toggle="tab">Framework Parameters</a>')
        self.assertContains(response, '<div class="tab-pane" id="framework_parameter">')


class ProjectNewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('queries:project_new')

        self.instance = Instance.objects.create(
            url='http://jira.west.com',
            jira_user='readonly_sliu_api_user',
            password='qualityengineering',
            jira_fields=['components', 'status', 'priority', 'versions', 'issuetype']
        )
        self.impact_map = ImpactMap.objects.create(
            name='Apps'
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

    def test_project_new_url_resolve_to_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func, project_new)

    def test_project_new_url_returns_status_200(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_project_new_invalid_with_normal_user(self):
        data = {
            'name': 'Temp Project',
            'jira_key': 'Key',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
        }
        response = self.client.post(self.url, data)
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(name=data['name'])

    def test_project_new_valid_with_super_user(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        data = {
            'name': 'Temp Project',
            'jira_key': 'Key',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
            'component_field': Project.COMPONENT
        }
        response = self.client.post(self.url, data)
        project = Project.objects.get(name=data['name'])
        self.assertIsNotNone(project)

    def test_project_new_invalid_with_blank_name(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        data = {
            'name': '',
            'jira_key': 'Key',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'Correct errors in the project new form.')

    def test_project_new_invalid_with_blank_jira_key(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        data = {
            'name': 'Temp Project',
            'jira_key': '',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'Correct errors in the project new form.')

    def test_project_new_invalid_with_blank_instance(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        data = {
            'name': 'Temp Project',
            'jira_key': 'Key',
            'instance': None,
            'impact_map': self.impact_map.id,
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'Correct errors in the project new form.')

    def test_project_new_invalid_with_blank_impact_map(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        data = {
            'name': 'Temp Project',
            'jira_key': 'Key',
            'instance': self.instance.id,
            'impact_map': None,
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'Correct errors in the project new form.')


class ProjectDetailTest(TestCase):
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

    def test_project_detail_resolve_to_view(self):
        found = resolve(reverse('queries:project_detail', args=[self.project.id, ]))
        self.assertEqual(found.func, project_detail)

    def test_project_detail_successful_with_valid_id(self):
        response = self.client.get(reverse('queries:project_detail', args=[self.project.id, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)

    def test_project_detail_unsuccessful_with_invalid_id(self):
        response = self.client.get(reverse('queries:project_detail', args=[100, ]))
        self.assertEqual(response.status_code, 404)

    def test_project_detail_contains_4_tabs(self):
        response = self.client.get(reverse('queries:project_detail', args=[self.project.id, ]))
        self.assertContains(response, '<a href="#include_uat" data-toggle="tab">Overall</a>')
        self.assertContains(response, '<a href="#exclude_uat" data-toggle="tab">Internal Testing</a>')
        self.assertContains(response, '<a href="#only_uat" data-toggle="tab">UAT</a>')
        self.assertContains(response, '<a href="#custom" data-toggle="tab">Custom</a>')


class ProjectEditTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.instance = Instance.objects.create(
            url='http://jira.west.com',
            jira_user='readonly_sliu_api_user',
            password='qualityengineering',
            jira_fields=['components', 'status', 'priority', 'versions', 'issuetype', 'resolution', 'created', 'customfield_13286', 'customfield_10092', 'customfield_13890']
        )
        self.impact_map = ImpactMap.objects.create(
            name='Apps'
        )
        self.project = Project.objects.create(
            name='Temp Project',
            jira_key='TP',
            jira_version='1.0',
            instance=self.instance,
            impact_map=self.impact_map,
        )
        self.project_exist = Project.objects.create(
            name='Exist Project',
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

    def test_project_edit_resolve_to_view(self):
        found = resolve(reverse('queries:project_edit', args=[self.project.id, ]))
        self.assertEqual(found.func, project_edit)

    def test_project_edit_successful_with_valid_id(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        response = self.client.post(reverse('queries:project_edit', args=[self.project.id, ]))
        self.assertEqual(response.status_code, 200)

    def test_project_edit_unsuccessful_with_invalid_id(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        response = self.client.post(reverse('queries:project_edit', args=[100, ]))
        self.assertEqual(response.status_code, 404)

    def test_project_edit_redirect_to_projects_list_without_post_method(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        response = self.client.get(reverse('queries:project_edit', args=[self.project.id, ]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('queries:projects'))

    def test_project_edit_successful_with_valid_data(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        data = {
            'name': 'Edit Temp Project',
            'jira_key': 'TP',
            'jira_version': '1.0',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
            'component_field': Project.COMPONENT,
            'active': True,
            'complete': False
        }
        response = self.client.post(reverse('queries:project_edit', args=[self.project.id, ]), data, follow=True)
        self.assertEqual(response.status_code, 200)
        project = Project.objects.get(name=data['name'])
        self.assertIsNotNone(project)

    def test_project_edit_unsuccessful_with_blank_data(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        response = self.client.post(reverse('queries:project_edit', args=[self.project.id, ]))
        self.assertContains(response, 'Correct errors in the form')
        self.assertContains(response, 'Name:</label></th><td><ul class="errorlist"><li>This field is required.</li>')
        self.assertContains(response, 'Jira key:</label></th><td><ul class="errorlist"><li>This field is required.')
        self.assertContains(response, 'Jira version:</label></th><td><ul class="errorlist"><li>This field is required')
        self.assertContains(response, 'Instance:</label></th><td><ul class="errorlist"><li>This field is required')
        self.assertContains(response, 'Impact map:</label></th><td><ul class="errorlist"><li>This field is required')

    def test_project_edit_redirect_detail_with_valid_data(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        data = {
            'name': 'Edit Temp Project',
            'jira_key': 'TP',
            'jira_version': '1.0',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
            'component_field': Project.COMPONENT,
            'active': True,
            'complete': False
        }
        response = self.client.post(reverse('queries:project_edit', args=[self.project.id, ]), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('queries:project_detail', args=[self.project.id, ]))

    def test_project_edit_unsuccessful_with_duplicate_name(self):
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )
        data = {
            'name': 'Exist Project',
            'jira_key': 'TP',
            'jira_version': '1.0',
            'instance': self.instance.id,
            'impact_map': self.impact_map.id,
            'active': True,
            'complete': False
        }
        response = self.client.post(reverse('queries:project_edit', args=[self.project.id, ]), data, follow=True)
        self.assertContains(response, 'Correct errors in the form')
        self.assertContains(response, 'Project with this Name already exists.')


class ProjectDeleteTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.instance = Instance.objects.create(
            url='http://jira.west.com',
            jira_user='readonly_sliu_api_user',
            password='qualityengineering',
            jira_fields=['components', 'status', 'priority', 'versions', 'issuetype', 'resolution', 'created', 'customfield_13286', 'customfield_10092', 'customfield_13890']
        )
        self.impact_map = ImpactMap.objects.create(
            name='Apps'
        )
        self.project = Project.objects.create(
            name='Temp Project',
            jira_key='TP',
            jira_version='1.0',
            instance=self.instance,
            impact_map=self.impact_map,
        )
        self.project_exist = Project.objects.create(
            name='Exist Project',
            jira_key='TP',
            jira_version='1.0',
            instance=self.instance,
            impact_map=self.impact_map
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
        self.client.login(
            username=self.superuser_account['username'],
            password=self.superuser_account['password']
        )

    def test_project_delete_resolve_to_view(self):
        found = resolve(reverse('queries:project_delete', args=[self.project.id, ]))
        self.assertEqual(found.func, project_delete)

    def test_project_delete_successful_with_valid_id(self):
        response = self.client.post(reverse('queries:project_delete', args=[self.project_exist.id, ]), follow=True)
        self.assertEqual(response.status_code, 200)
        projects = Project.objects.filter(name='Exist Project')
        self.assertEqual(projects.count(), 0)

    def test_project_delete_unsuccessful_with_invalid_id(self):
        response = self.client.post(reverse('queries:project_delete', args=[100, ]))
        self.assertEqual(response.status_code, 404)

    def test_project_delete_redirect_to_projects_with_successful(self):
        response = self.client.post(reverse('queries:project_delete', args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('queries:projects'))

