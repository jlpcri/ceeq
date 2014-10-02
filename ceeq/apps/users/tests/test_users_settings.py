from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve

from ceeq.apps.users.views import user_settings


class UsersSettingsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('user_settings')
        self.user_account_correct = {
            'username': 'correctName',
            'password': 'correctPassword'
        }
        self.user = User.objects.create_user(
            username=self.user_account_correct['username'],
            password=self.user_account_correct['password']
        )

    def test_user_settings_resolve_to_view(self):
        found = resolve(reverse('user_settings'))
        self.assertEqual(found.func, user_settings)

    def test_user_settings_successful_with_signin(self):
        self.client.login(
            username=self.user_account_correct['username'],
            password=self.user_account_correct['password']
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_settings_unsuccessful_without_signin(self):
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, reverse('landing'))