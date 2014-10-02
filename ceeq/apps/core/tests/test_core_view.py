from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve

from ceeq.apps.core.views import landing


class CoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('landing')

    def test_landing_url_resolve_to_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func, landing)

    def test_landing_url_returns_status_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)