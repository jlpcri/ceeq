from django.core.management.base import BaseCommand, CommandError

from ceeq.apps.queries.tasks import daily_score_log


class Command(BaseCommand):
    args = '<None>'
    help = 'Save daily Combined/Internal/UAT score per project'

    def handle(self, *args, **options):
        daily_score_log()

        self.stdout.write("Daily CEEQ Score updated to ScoreHistory.")

