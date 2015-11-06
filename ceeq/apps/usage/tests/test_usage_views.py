from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve, reverse
from datetime import datetime
import pytz

from ceeq.apps.usage.models import ProjectAccess
from ceeq.apps.usage.views import update_project_access_history, usage


class ProjectAccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.project_access = ProjectAccess.objects.create(
            created=datetime.utcnow().replace(tzinfo=pytz.utc),
            total=100
        )
        self.user_account = {
            'username': 'correctName',
            'password': 'correctPassword'
        }
        self.user = User.objects.create_user(
            username=self.user_account['username'],
            password=self.user_account['password']
        )
        # self.client.login(
        #     username=self.user_account['username'],
        #     password=self.user_account['password']
        # )
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

    def test_project_access_url_resolve_to_view(self):
        found = resolve(reverse('usage:usage'))
        self.assertEqual(found.func, usage)

    def test_project_access_return_200(self):
        response = self.client.get(reverse('usage:usage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="/ceeq/usage/"><i class="fa fa-table fa-fw"></i>Usage</a>')
        self.assertContains(response, '<a href="/ceeq/usage/project_access_update/"><i class="fa fa-refresh"></i></a>')

    def test_project_access_invalid_with_normal_user(self):
        self.client.login(
            username=self.user_account['username'],
            password=self.user_account['password']
        )
        response = self.client.get(reverse('usage:usage'))
        self.assertNotContains(response, '<a href="/ceeq/usage/"><i class="fa fa-table fa-fw"></i>Usage</a>')
        self.assertNotContains(response, '<a href="/ceeq/usage/project_access_update/"><i class="fa fa-refresh"></i></a>')

