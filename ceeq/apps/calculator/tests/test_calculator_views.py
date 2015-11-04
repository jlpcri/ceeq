from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse

from ceeq.apps.calculator.models import ImpactMap
from ceeq.apps.calculator.views import calculate_score_all
from ceeq.apps.queries.models import Project, Instance


class CalculatorViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.instance = Instance.objects.create(
            url='http://jira.west.com',
        )
        self.impact_map = ImpactMap.objects.create(
            name='Apps'
        )

        self.project = Project.objects.create(
            name='Temp Project',
            jira_key='TP',
            instance=self.instance,
            impact_map=self.impact_map,
        )

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

    def test_calculate_score_all_url_resolve_to_view(self):
        found = resolve(reverse('calculator:calculate_score_all'))
        self.assertEqual(found.func, calculate_score_all)

    def test_calculate_score_all_url_returns_status_200(self):
        response = self.client.get(reverse('calculator:calculate_score_all'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_calculate_score_all_works_with_superuser_signin(self):
        self.client.login(
            username=self.superuser_account_correct['username'],
            password=self.superuser_account_correct['password']
        )
        response = self.client.get(reverse('calculator:calculate_score_all'), follow=True)

        self.assertContains(response, self.project.name)

    def test_calculate_score_all_not_works_without_signin(self):
        response = self.client.get(reverse('calculator:calculate_score_all'), follow=True)

        self.assertNotContains(response, self.project.name)
        self.assertContains(response, 'Please use your Active Directory credentials.')