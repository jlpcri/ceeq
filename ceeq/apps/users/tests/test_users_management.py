from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve

from ceeq.apps.users.views import user_management


class UsersManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('users:management')
        self.user_account_superuser = {
            'username': 'superUserName',
            'password': 'superUserPassword'
        }
        self.user_account_normaluser = {
            'username': 'normalUserName',
            'password': 'normalUserPassword'
        }
        self.user_superuser = User.objects.create_superuser(
            username=self.user_account_superuser['username'],
            password=self.user_account_superuser['password'],
            email=''
        )
        self.user_normaluser = User.objects.create(
            username=self.user_account_normaluser['username'],
            password=self.user_account_normaluser['password']
        )

    def test_user_management_resolve_to_view(self):
        found = resolve(reverse('users:management'))
        self.assertEqual(found.func, user_management)

    def test_user_management_successful_with_superuser(self):
        self.client.login(
            username=self.user_account_superuser['username'],
            password=self.user_account_superuser['password']
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_management_unsuccessful_with_normaluser(self):
        self.client.login(
            username=self.user_account_normaluser['username'],
            password=self.user_account_normaluser['password']
        )
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, reverse('landing'))