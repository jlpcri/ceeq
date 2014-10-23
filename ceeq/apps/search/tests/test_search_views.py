from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse

from ceeq.apps.projects.models import Project
from ceeq.apps.search.views import search


class SearchViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('search')
        self.project_search_first = {
            'name': 'first project',
            'jira_name': 'first JIRA',
            'jira_version': 'All Versions',
            'score': 5
        }
        self.project_first = Project.objects.create(
            name=self.project_search_first['name'],
            jira_name=self.project_search_first['jira_name'],
            jira_version=self.project_search_first['jira_version'],
            score=self.project_search_first['score']
        )
        self.project_search_second = {
            'name': 'second project',
            'jira_name': 'second JIRA'
        }
        self.project_second = Project.objects.create(
            name=self.project_search_second['name'],
            jira_name=self.project_search_second['jira_name']
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
        self.assertContains(self.response, reverse('project_detail',
                                                   args=[str(self.project_first.id)]))

    def test_search_results_contains_correct_url_to_defects_density(self):
        self.assertContains(self.response, reverse('project_defects_density',
                                                   args=[str(self.project_first.id)]))

    def test_search_results_contains_correct_url_to_update_score(self):
        self.assertContains(self.response, reverse('project_update_scores',
                                                   args=[str(self.project_first.id)]))

    def test_results_contains_correct_url_to_jira(self):
        self.assertContains(self.response, 'http://jira.west.com/browse/' + self.project_first.jira_name)