from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse

from ceeq.apps.queries.models import Project, Instance
from ceeq.apps.calculator.models import ImpactMap
from ceeq.apps.search.views import search


class SearchViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.instance = Instance.objects.create(
            url='http://jira.west.com',
        )
        self.impact_map = ImpactMap.objects.create(
            name='Apps'
        )
        self.url = reverse('search:search')
        self.project_search_first = {
            'name': 'first project',
            'jira_key': 'firstJIRA',
            'jira_version': 'All Versions',
            'instance': self.instance,
            'impact_map': self.impact_map
        }
        self.project_first = Project.objects.create(
            name=self.project_search_first['name'],
            jira_key=self.project_search_first['jira_key'],
            jira_version=self.project_search_first['jira_version'],
            instance=self.project_search_first['instance'],
            impact_map=self.project_search_first['impact_map']
        )
        self.project_search_second = {
            'name': 'second project',
            'jira_key': 'secondJIRA',
            'jira_version': 'All Versions',
            'instance': self.instance,
            'impact_map': self.impact_map
        }
        self.project_second = Project.objects.create(
            name=self.project_search_second['name'],
            jira_key=self.project_search_second['jira_key'],
            jira_version=self.project_search_second['jira_version'],
            instance=self.project_search_second['instance'],
            impact_map=self.project_search_second['impact_map']
        )
        self.response = self.client.get(
            self.url,
            {'query': 'first'}
        )

    def test_search_url_resolve_to_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func, search)

    def test_search_url_returns_status_200(self):
        response = self.client.get(
            self.url,
            {'query': ''}
        )
        self.assertEqual(response.status_code, 200)

    def test_search_results_return_with_correct_query(self):
        self.assertContains(self.response, self.project_first.name)
        self.assertNotContains(self.response, self.project_second.name)

    def test_search_all_results_return_with_empty_string_query(self):
        response = self.client.get(
            self.url,
            {'query': ''}
        )
        self.assertContains(response, self.project_first.name)
        self.assertContains(response, self.project_second.name)

    def test_search_not_results_return_with_incorrect_query(self):
        response = self.client.get(
            self.url,
            {'query': 'incorrect'}
        )
        self.assertNotContains(response, self.project_first.name)
        self.assertNotContains(response, self.project_second.name)

    def test_search_results_contains_correct_url_to_project(self):
        self.assertContains(self.response, reverse('queries:project_detail',
                                                   args=[str(self.project_first.id)]))

    def test_results_contains_correct_url_to_jira(self):
        self.assertContains(self.response, self.instance.url + '/issues/?jql=project=' + self.project_first.jira_key)