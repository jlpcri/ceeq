from django.test import TestCase

from ceeq.apps.projects.models import Project, ProjectComponentsDefectsDensity


class ProjectModelTests(TestCase):
    def create_project(self):
        self.name = 'Test Project'
        self.jira_name = 'Test JIRA Name'
        self.project = Project.objects.create(
            name=self.name,
            jira_name=self.jira_name,
        )
        return self.project

    def test_project_with_name(self):
        project = self.create_project()
        self.assertTrue(isinstance(project, Project))
        self.assertEqual(project.__unicode__(), project.name)


class ProjectComponentsDefectsDensityModelTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name='Test Project',
            jira_name='Test JIRA Name',
        )

    def create_pcdd(self):
        self.version = 'All Versions'
        self.pcdd = ProjectComponentsDefectsDensity.objects.create(
            project=self.project,
            version=self.version,
        )
        return self.pcdd

    def test_pcdd_with_project_name(self):
        pcdd = self.create_pcdd()
        self.assertTrue(isinstance(pcdd, ProjectComponentsDefectsDensity))
        self.assertEqual(pcdd.__unicode__(), pcdd.project.name)
