from django.core.management.base import BaseCommand, CommandError
from ceeq.apps.projects.models import Project, ProjectComponentsDefectsDensity

from ceeq.apps.projects.views import defects_density_single_log, calculate_score


class Command(BaseCommand):
    args = '<project_id project_id ...>'
    help = 'Save daily components defect impact to specified project'

    def handle(self, *args, **options):
        if args:
            for project_id in args:
                try:
                    project = Project.objects.get(pk=project_id)
                except Project.DoesNotExist:
                    raise CommandError('Project "%s" does not exist' % project_id)
                calculate_score(None, project)
                defects_density_single_log(None, project)
                self.stdout.write('Successfully updated score and saved Defect Impact for project "%s"' % project.name)
        else:
            projects_active = Project.objects.filter(complete=False).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
            for project in projects_active:
                calculate_score(None, project)
                defects_density_single_log(None, project)

            self.stdout.write("All active projects Score updated, and Defect Impact saved")

