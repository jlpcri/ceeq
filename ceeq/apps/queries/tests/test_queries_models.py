from django.test import TestCase
from datetime import datetime
import pytz

from ceeq.apps.queries.models import Instance, Project, ScoreHistory, ImpactMap


class InstanceModelTest(TestCase):
    def test_string_representation(self):
        instance = Instance(
            url='http://jira.west.com'
        )
        self.assertEqual(str(instance), instance.url)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Instance._meta.verbose_name_plural), 'instances')


class ScoreHistoryModelTest(TestCase):
    def setUp(self):
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

    def test_string_representation(self):
        score_history = ScoreHistory(
            project=self.project,
            created=datetime.utcnow().replace(tzinfo=pytz.utc)
        )
        self.assertEqual(str(score_history), '{0}: {1}: {2}: {3}'.format(score_history.project.name,
                                                                    score_history.created,
                                                                    score_history.internal_score,
                                                                    score_history.access))

    def test_verbose_name_plural(self):
        self.assertEqual(str(ScoreHistory._meta.verbose_name_plural), 'score historys')


class ProjectModelTest(TestCase):
    def setUp(self):
        self.instance = Instance.objects.create(
            url='http://jira.west.com',
            jira_user='readonly_sliu_api_user',
            password='qualityengineering',
            jira_fields=['components', 'status', 'priority', 'versions', 'issuetype']
        )
        self.impact_map = ImpactMap.objects.create(
            name='Apps'
        )
        self.project = Project(
            name='Temp Project',
            jira_key='TP',
            instance=self.instance,
            impact_map=self.impact_map
        )

    def test_string_representation(self):
        self.assertEqual(str(self.project), '{0}: {1}: {2}'.format(self.project.name,
                                                                   self.project.jira_key,
                                                                   self.project.jira_version))

    def test_verbose_name_plural(self):
        self.assertEqual(str(Project._meta.verbose_name_plural), 'projects')

    def test_fetch_jira_data(self):
        data = self.project.fetch_jira_data
        self.assertTrue(len(data['issues']) > 0)

    def test_fetch_jira_versions(self):
        versions = self.project.fetch_jira_versions
        self.assertTrue(len(versions) > 1)  # At least has 'All Versions'

    def test_project_internal_score(self):
        score = self.project.internal_score
        self.assertEqual(score, 0)

    def test_project_uat_score(self):
        score = self.project.uat_score
        self.assertEqual(score, 0)

    def test_project_combined_score(self):
        score = self.project.overall_score
        self.assertEqual(score, 0)