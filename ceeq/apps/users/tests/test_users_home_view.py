from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve

from ceeq.apps.users.views import home


class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('users:home')

        self.user_account = {
            'username': 'correctName',
            'password': 'correctPassword'
        }
        self.user = User.objects.create_user(
            username=self.user_account['username'],
            password=self.user_account['password']
        )

    def test_home_url_resolve_to_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func, home)

    def test_home_url_returns_redirect_without_signin(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_home_url_returns_successful_with_signin(self):
        self.client.login(
            username=self.user_account['username'],
            password=self.user_account['password']
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Comprehensive End to End Quality</h1>')
        self.assertContains(response, '<li>A new metric framework to describe the measurement of West Developed Solutions</li>')
        self.assertContains(response, '<li>A new standard to evaluate the impact of solution defects on the overall quality of the IVR solutions</li>')
        self.assertContains(response, '<li>A brand new framework to target the components of West Developed Solutions</li>')
        self.assertContains(response, '<li>CEEQ score ranges from 0 (product broken) to 10 (product with no known defects)</li>')

