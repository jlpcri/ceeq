from django.test import TestCase, Client
from django.core.urlresolvers import reverse, resolve

from django.contrib.auth.models import User
from ceeq.apps.users.views import sign_in, sign_out


class TestUsersAuthenticationSignIn(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_account_correct = {
            'username': 'correctName',
            'password': 'correctPassword'
        }
        self.user = User.objects.create_user(
            username=self.user_account_correct['username'],
            password=self.user_account_correct['password']
        )
        self.user_account_incorrect_username = {
            'username': 'incorrectName',
            'password': 'correctPassword'
        }
        self.user_account_incorrect_password = {
            'username': 'correctName',
            'password': 'incorrectPassword'
        }

    def test_user_sign_in_resolve_to_view(self):
        found = resolve(reverse('users:sign_in'))
        self.assertEqual(found.func, sign_in)

    def test_user_sign_in_successfully_redirect(self):
        response = self.client.post(
            reverse('users:sign_in'),
            self.user_account_correct
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:home'))

    def test_user_sign_in_unsuccessfully_with_incorrect_username_redirect(self):
        response = self.client.post(
            reverse('users:sign_in'),
            self.user_account_incorrect_username
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))

    def test_user_sign_in_unsuccessfully_with_incorrect_password_redirect(self):
        response = self.client.post(
            reverse('users:sign_in'),
            self.user_account_incorrect_password
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))

    def test_user_sign_in_successfully(self):
        response = self.client.post(
            reverse('users:sign_in'),
            self.user_account_correct,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_user_sign_in_unsuccessfully_with_incorrect_username(self):
        response = self.client.post(
            reverse('users:sign_in'),
            self.user_account_incorrect_username,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        message = list(response.context['messages'])
        self.assertEqual(str(message[0]), 'Invalid username or password.')

    def test_user_sign_in_unsuccessfully_with_incorrect_password(self):
        response = self.client.post(
            reverse('users:sign_in'),
            self.user_account_incorrect_password,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        message = list(response.context['messages'])
        self.assertEqual(str(message[0]), 'Invalid username or password.')

    def test_user_sign_in_unsuccessfully_without_post_method(self):
        response = self.client.get(
            reverse('users:sign_in'),
            self.user_account_correct
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)


class TestUsersAuthenticationSignOut(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_account_correct = {
            'username': 'correctName',
            'password': 'correctPassword'
        }
        self.user = User.objects.create_user(
            username=self.user_account_correct['username'],
            password=self.user_account_correct['password']
        )
        self.client.login(
            username=self.user_account_correct['username'],
            password=self.user_account_correct['password']
        )

    def test_user_sign_out_resolve_to_view(self):
        found = resolve(reverse('users:sign_out'))
        self.assertEqual(found.func, sign_out)

    def test_user_sign_out_redirect(self):
        response = self.client.post(
            reverse('users:sign_out')
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))

    def test_user_sign_out_successfully(self):
        response = self.client.post(
            reverse('users:sign_out'),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('auth_user_id', self.client.session)