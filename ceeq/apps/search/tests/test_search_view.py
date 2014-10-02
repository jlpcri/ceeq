from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse

from ceeq.apps.projects.models import Project
from ceeq.apps.search.views import search


class SearchViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('search')
        self.project_search = {
            'name': 'searchProjectName',
            'jira_name': 'searchProjectJiraName'
        }
        self.project = Project.objects.create(
            name=self.project_search['name'],
            jira_name=self.project_search['jira_name']
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

    def test_search_successfully_with_correct_query(self):
        response = self.client.get(
            self.url,
            {'query': 'search'}
        )
        self.assertContains(response, self.project.name)

    def test_search_unsuccessfully_with_incorrect_query(self):
        response = self.client.get(
            self.url,
            {'query': 'incorrect'}
        )
        self.assertNotContains(response, self.project.name)