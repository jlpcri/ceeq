from datetime import date
from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse

from ceeq.apps.projects.models import Project, ProjectComponentsDefectsDensity
from ceeq.apps.defects_density.views import dd_all, dd_detail


class DefectsDensityViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.project = Project.objects.create(
            name='exampleProject',
            jira_name='exampleJiraNameProject'
        )
        self.dd_single = ProjectComponentsDefectsDensity.objects.create(
            project=self.project,
            version='1.1',
            created=date.today()
        )

        self.url_dd_all = reverse('dd_all')
        self.url_dd_detail = reverse(
            'dd_detail',
            kwargs={'dd_id': self.dd_single.id}
        )

    def test_defects_density_all_url_resolve_to_view(self):
        found = resolve(self.url_dd_all)
        self.assertEqual(found.func, dd_all)

    def test_defects_density_all_url_returns_status_200(self):
        response = self.client.get(self.url_dd_all)
        self.assertEqual(response.status_code, 200)

    def test_defects_density_detail_url_resolve_to_view(self):
        found = resolve(self.url_dd_detail)
        self.assertEqual(found.func, dd_detail)

    def test_defects_density_detail_url_returns_status_200(self):
        response = self.client.get(self.url_dd_detail)
        self.assertEqual(response.status_code, 200)