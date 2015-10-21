from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Starts the background task to run queries against JIRA for all current projects'

    def handle(self, *args, **options):
        print "Someday, I'll be a real boy!"
