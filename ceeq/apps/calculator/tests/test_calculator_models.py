from datetime import datetime
import pytz
from django.test import TestCase
from django.utils.timezone import localtime

from ceeq.apps.calculator.models import ImpactMap, ComponentImpact, SeverityMap, ComponentComplexity, ResultHistory, LiveSettings
from ceeq.apps.queries.models import Project, Instance


class ImpactMapModelTest(TestCase):
    def test_string_representation(self):
        impact_map = ImpactMap(
            name='Test Impact Map'
        )
        self.assertEqual(str(impact_map), impact_map.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(ImpactMap._meta.verbose_name_plural), 'impact maps')


class ComponentImpactModelTest(TestCase):
    def setUp(self):
        self.impact_map = ImpactMap(
            name='Default Impact Map'
        )

    def test_string_representation(self):
        component_impact = ComponentImpact(
            impact_map=self.impact_map,
            component_name='Test Component Name',
        )
        self.assertEqual(str(component_impact), '{0}: {1}: {2}'.format(component_impact.impact_map.name,
                                                                       component_impact.component_name,
                                                                       component_impact.impact))

    def test_verbose_name_plural(self):
        self.assertEqual(str(ComponentImpact._meta.verbose_name_plural), 'component impacts')


class SeverityMapModelTest(TestCase):
    def test_string_representation(self):
        severity_map = SeverityMap(
            name='Test Severity Map'
        )
        self.assertEqual(str(severity_map), severity_map.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(SeverityMap._meta.verbose_name_plural), 'severity maps')


class ComponentComplexityModelTest(TestCase):
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
        component_complexity = ComponentComplexity(
            project=self.project,
            component_name='Test Component Name'
        )
        self.assertEqual(str(component_complexity), '{0}: {1}'.format(component_complexity.project.name,
                                                                      component_complexity.component_name))

    def test_verbose_name_plural(self):
        self.assertEqual(str(ComponentComplexity._meta.verbose_name_plural), 'component complexitys')


class ResultHistoryModelTest(TestCase):
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
        result_history = ResultHistory(
            project=self.project,
            created=datetime.utcnow().replace(tzinfo=pytz.utc),
            confirmed=datetime.utcnow().replace(tzinfo=pytz.utc)
        )
        self.assertEqual(str(result_history), '{0}: {1}: {2}'.format(result_history.project.name,
                                                                     localtime(result_history.confirmed),
                                                                     localtime(result_history.created)))

    def test_verbose_name_plural(self):
        self.assertEqual(str(ResultHistory._meta.verbose_name_plural), 'result historys')


class LiveSettingsModelTest(TestCase):
    def test_string_representatin(self):
        live_settings = LiveSettings(
            score_scalar=50,
            current_delay=100
        )
        self.assertEqual(str(live_settings), '{0}: {1}'.format(live_settings.score_scalar, live_settings.current_delay))

    def test_verbose_name_plural(self):
        self.assertEqual(str(LiveSettings._meta.verbose_name_plural), 'live settingss')
