from django.core.management.base import BaseCommand, CommandError
from ceeq.apps.projects.models import Project, ProjectComponentsDefectsDensity


class Command(BaseCommand):
    args = '<project_id project_id ...>'
    help = 'Save daily components defects density to specified project'

    def handle(self, *args, **options):
        for project_id in args:
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                raise CommandError('Project "%s" does not exist' % project_id)
            print project.name
            self.stdout.write('Successfully "%s"' % project_id)

