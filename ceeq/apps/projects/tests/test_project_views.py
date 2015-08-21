from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse

from ceeq.apps.projects.models import Project, ProjectType
from ceeq.apps.projects.views import projects, project_new, project_detail, project_edit, project_delete, \
    project_defects_density, project_update_scores, defects_density_log
from ceeq.apps.users.models import UserSettings


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
        self.assertQuerysetEqual(response.context['projects_active'], [])
        self.assertQuerysetEqual(response.context['projects_archive'], [])

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
        self.project_type = ProjectType.objects.create(name='Apps')
        self.new_project_valid = {
            'name': 'New Project',
            'jira_name': 'New Jira Name',
            'project_type': 1
        }
        self.new_project_invalid_without_name = {
            'name': '',
            'jira_name': 'New Jira Name',
        }
        self.new_project_invalid_without_jira_name = {
            'name': 'New Project',
            'jira_name': '',
        }
        self.new_project_invalid_with_duplicate_name = {
            'name': 'New Project',
            'jira_name': 'Not Duplicate Jira Name',
        }
        self.superuser_account_correct = {
            'username': 'superUserName',
            'password': 'superUserPassword',
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
        response = self.client.post(self.url, self.new_project_invalid_without_name)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Correct errors in the form.')

    def test_project_new_without_jira_name_gives_required_error(self):
        response = self.client.post(self.url, self.new_project_invalid_without_jira_name)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Correct errors in the form.')

    def test_project_new_with_duplicate_name_gives_required_error(self):
        response = self.client.post(self.url, self.new_project_valid, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url, self.new_project_invalid_with_duplicate_name, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Correct errors in the form.')


class ProjectDetailTests(TestCase):
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

    def test_project_detail_resolves_to_view(self):
        found = resolve(reverse('project_detail',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, project_detail)

    def test_project_detail_with_valid_id_successful(self):
        response = self.client.get(reverse('project_detail',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project['name'])

    def test_project_detail_with_invalid_id_unsuccessful(self):
        response = self.client.get(reverse('project_detail',
                                           args=[100, ]))
        self.assertEqual(response.status_code, 404)


class ProjectEditTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = {
            'name': 'Existing Project',
            'jira_name': 'Existing Jira Name'
        }
        self.project_type = ProjectType.objects.create(name='Apps')
        self.project_exist = Project.objects.create(name=self.project['name'],
                                                    jira_name=self.project['jira_name'],
                                                    project_type=self.project_type)

        self.project_edit = {
            'name': 'Editing Project',
            'jira_name': 'Editing Jira Name',
            'jira_version': 'Editing Versions',
            'project_type': 1
        }
        self.project_edit_empty_name = {
            'name': '',
            'jira_name': 'Editing Jira Name',
            'jira_version': 'Editing Versions'
        }
        self.project_edit_empty_jira_name = {
            'name': 'Editing Project',
            'jira_name': '',
            'jira_version': 'Editing Versions'
        }
        self.project_edit_empty_jira_version = {
            'name': 'Editing Project',
            'jira_name': 'Editing Jira Name',
            'jira_version': '',
        }

        self.superuser_account_correct = {
            'username': 'superUserName',
            'password': 'superUserPassword',
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

    def test_project_edit_resolves_to_view(self):
        found = resolve(reverse('project_edit',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, project_edit)

    def test_project_edit_with_invalid_id_unsuccessful(self):
        response = self.client.get(reverse('project_edit',
                                           args=[100, ]))
        self.assertEqual(response.status_code, 404)

    def test_project_edit_with_other_than_post_method_redirect_project_lists(self):
        response = self.client.get(reverse('project_edit',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('projects'))

    def test_project_edit_with_valid_data_successful(self):
        response = self.client.post(reverse('project_edit',
                                            args=[self.project_exist.id, ]),
                                    self.project_edit)
        project = Project.objects.get(name=self.project_edit['name'])
        self.assertIsNotNone(project)

    def test_project_edit_with_valid_data_redirect_to_project_detail(self):
        response = self.client.post(reverse('project_edit',
                                            args=[self.project_exist.id, ]),
                                    self.project_edit)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('project_detail',
                                               args=[self.project_exist.id, ]))

    def test_project_edit_with_empty_name_gives_error(self):
        response = self.client.post(reverse('project_edit',
                                            args=[self.project_exist.id, ]),
                                    self.project_edit_empty_name)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Correct errors in the form.')

    def test_project_edit_with_empty_jira_name_gives_error(self):
        response = self.client.post(reverse('project_edit',
                                            args=[self.project_exist.id, ]),
                                    self.project_edit_empty_jira_name)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Correct errors in the form.')

    def test_project_edit_with_empty_jira_version_gives_error(self):
        response = self.client.post(reverse('project_edit',
                                            args=[self.project_exist.id, ]),
                                    self.project_edit_empty_jira_version)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Correct errors in the form.')


class ProjectDeleteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = {
            'name': 'Existing Project',
            'jira_name': 'Existing Jira Name'
        }
        self.project_exist = Project.objects.create(name=self.project['name'],
                                                    jira_name=self.project['jira_name'])

        self.superuser_account_correct = {
            'username': 'superUserName',
            'password': 'superUserPassword',
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

    def test_project_delete_resolves_to_view(self):
        found = resolve(reverse('project_delete',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, project_delete)

    def test_project_delete_with_valid_id_successful(self):
        response = self.client.get(reverse('project_delete',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 302)
        projects = Project.objects.filter(name=self.project['name'])
        self.assertEqual(projects.count(), 0)

    def test_project_delete_with_valid_redirect_to_project_list(self):
        response = self.client.get(reverse('project_delete',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('projects'))

    def test_project_delete_with_invalid_id_unsuccessful(self):
        response = self.client.get(reverse('project_delete',
                                           args=[100, ]))
        self.assertEqual(response.status_code, 404)


class ProjectDefectsDensityTests(TestCase):
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

    def test_project_defects_density_url_resolves_to_view(self):
        found = resolve(reverse('project_defects_density',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, project_defects_density)

    def test_project_defects_density_with_valid_id_returns_200(self):
        response = self.client.get(reverse('project_defects_density',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Current Defect Impact')
        self.assertContains(response, 'Trending Defect Impact')
        self.assertContains(response, 'Trending CEEQ Score')
        self.assertContains(response, 'History Defect Impact')
        self.assertContains(response, self.project['name'])

    def test_project_defects_density_with_invalid_id_gives_error(self):
        response = self.client.get(reverse('project_defects_density',
                                           args=[100, ]))
        self.assertEqual(response.status_code, 404)

    #Following relate to project update scores

    def test_project_update_scores_url_resolves_to_view(self):
        found = resolve(reverse('project_update_scores',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, project_update_scores)

    def test_project_update_scores_with_valid_id_returns_200(self):
        response = self.client.get(reverse('project_update_scores',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Projects')
        self.assertContains(response, self.project['name'])

    def test_project_update_scores_with_invalid_id_gives_error(self):
        response = self.client.get(reverse('project_update_scores',
                                           args=[100, ]))
        self.assertEqual(response.status_code, 404)


class ProjectDefectsDensityLogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = {
            'name': 'Existing Project',
            'jira_name': 'Existing Jira Name'
        }
        self.project_exist = Project.objects.create(name=self.project['name'],
                                                    jira_name=self.project['jira_name'])

        self.superuser_account_correct = {
            'username': 'superUserName',
            'password': 'superUserPassword',
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

    def test_project_defects_density_log_url_resolves_view(self):
        found = resolve(reverse('defects_density_log',
                                args=[self.project_exist.id, ]))
        self.assertEqual(found.func, defects_density_log)

    def test_project_defects_density_log_with_valid_id_returns_200(self):
        response = self.client.get(reverse('defects_density_log',
                                           args=[self.project_exist.id, ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Projects')
        self.assertContains(response, self.project['name'])

    def test_project_defects_density_log_with_invalid_id_gives_error(self):
        response = self.client.get(reverse('defects_density_log',
                                           args=[100, ]))
        self.assertEqual(response.status_code, 404)


class ProjectUatTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = {
            'name': 'Test Project',
            'jira_name': 'tp'
        }
        self.project_type = ProjectType.objects.create(name='Apps')
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
        UserSettings.objects.create(
            user=self.user
        )

        self.client.login(
            username=self.user_account['username'],
            password=self.user_account['password']
        )

    def test_project_detail_uat_separation(self):
        response = self.client.get(reverse('project_detail',
                                       args=[self.project_exist.id, ]))

        self.assertContains(response, self.project['name'])
        self.assertContains(response, self.project['jira_name'])
        self.assertContains(response, '<a href="#include_uat" data-toggle="tab">Overall</a>')
        self.assertContains(response, '<a href="#exclude_uat" data-toggle="tab">Internal Testing</a>')
        self.assertContains(response, '<a href="#only_uat" data-toggle="tab">UAT</a>')
