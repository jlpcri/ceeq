from datetime import datetime
import pytz
from django.test import TestCase

from ceeq.apps.usage.models import ProjectAccess


class ProjectAccessModelTest(TestCase):
    def test_string_representation(self):
        project_access = ProjectAccess.objects.create(
            created=datetime.utcnow().replace(tzinfo=pytz.utc),
            total=100
        )
        self.assertEqual(str(project_access), '{0}: {1}'.format(project_access.created,
                                                                project_access.total))

    def test_verbose_name_plural(self):
        self.assertEqual(str(ProjectAccess._meta.verbose_name_plural), 'project accesss')