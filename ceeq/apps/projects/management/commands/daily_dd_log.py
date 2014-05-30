from django.core.management.base import BaseCommand, CommandError
from ceeq.apps.projects.models import Project, ProjectComponentsDefectsDensity


class Command(BaseCommand):
    args = '<project_id project_id ...>'
    help = 'Save daily components defects density to specified project'

    def handle(self, *args, **options):
        if args:
            for project_id in args:
                try:
                    project = Project.objects.get(pk=project_id)
                except Project.DoesNotExist:
                    raise CommandError('Project "%s" does not exist' % project_id)
                print project.name
                self.stdout.write('Successfully saved DD for project "%s"' % project_id)
        else:
            projects = Project.objects.all()
            for project in projects:
                print project.name
            self.stdout.write("All projects DD saved")

