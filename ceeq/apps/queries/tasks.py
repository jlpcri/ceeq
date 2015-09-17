from datetime import datetime
import time
from django.shortcuts import get_object_or_404
from celery import group

from ceeq import celery_app
from ceeq.apps.calculator.models import ResultHistory, LiveSettings
from models import Project


@celery_app.task
def fetch_jira_data_run():
    """
    Fetch jira data from jira instance and update/create ResultHistory object
    """
    projects = Project.objects.filter(complete=False)
    start = datetime.now()
    group(query_jira_data.delay(project.id) for project in projects)()
    end = datetime.now()

    current_delay = int((end - start).total_seconds())
    try:
        LiveSettings.objects.get(pk=1).current_delay = current_delay
    except LiveSettings.DoesNotExist:
        LiveSettings.objects.create(score_scalar=20,
                                    current_delay=current_delay)

    time.sleep(10)
    fetch_jira_data_run.delay()


@celery_app.task
def query_jira_data(project_id):
    project = get_object_or_404(Project, pk=project_id)
    jira_data = project.fetch_jira_data

    try:
        result = project.resulthistory_set.latest('confirmed')
        if result.query_results == jira_data['issues']:
            result.confirmed = datetime.now()
            result.save()
        else:
            result = ResultHistory.objects.create(
                project=project,
                # confirmed=datetime.now(),
                query_results=jira_data['issues'],
            )
    except ResultHistory.DoesNotExist:
        result = ResultHistory.objects.create(
            project=project,
            # confirmed=datetime.now(),
            query_results=[{
                'a': 'aa',
                'b': 'bb'
            }, {
                'c': 'cc',
                'd': 'dd'
            }],
        )

