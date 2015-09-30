from django.core.management.base import BaseCommand, CommandError

from ceeq.apps.calculator.views import calculate_score_all
from ceeq.apps.usage.views import update_project_access_history


class Command(BaseCommand):
    args = '<None>'
    help = 'Save daily Combined/Internal/UAT score per project'

    def handle(self, *args, **options):
        calculate_score_all(None)
        update_project_access_history(None)

        self.stdout.write("Daily CEEQ Score updated to ScoreHistory.")

