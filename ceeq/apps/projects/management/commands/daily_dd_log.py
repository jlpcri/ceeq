from django.core.management.base import BaseCommand, CommandError
from ceeq.apps.projects.models import Project, ProjectComponentsDefectsDensity

from ceeq.apps.projects.views import defects_density_single_log, calculate_score


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
                calculate_score(None, project)
                defects_density_single_log(None, project)
                self.stdout.write('Successfully updated score and saved Defects Density for project "%s"' % project.name)
        else:
            projects = Project.objects.all()
            for project in projects:
                if project.score < 0:
                    continue
                else:
                    calculate_score(None, project)
                    defects_density_single_log(None, project)

            self.stdout.write("All projects Score updated, and Defects Density saved")

