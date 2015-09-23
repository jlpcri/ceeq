from datetime import datetime
import time
from django.shortcuts import get_object_or_404
from celery import group

from ceeq import celery_app
from ceeq.apps.calculator.models import ResultHistory, LiveSettings
from ceeq.apps.queries.utils import parse_jira_data
from models import Project


@celery_app.task
def fetch_jira_data_run():
    """
    Fetch jira data from jira instance and update/create ResultHistory object
    """
    projects = Project.objects.filter(complete=False)
    start = datetime.now()
    current_delay = 0
    job = group(query_jira_data.s(project.id) for project in projects).delay()
    print "Job", job

    while True:
        if job.successful():
            print 'done'
            end = datetime.now()
            current_delay = int((end - start).total_seconds())
            print current_delay
            break
        print 'running'
        time.sleep(1)

    print current_delay

    try:
        ls = LiveSettings.objects.get(pk=1)
        ls.current_delay = current_delay
        ls.save()
    except LiveSettings.DoesNotExist:
        LiveSettings.objects.create(score_scalar=20,
                                    current_delay=current_delay)

    print "Start sleep"
    time.sleep(1)
    # fetch_jira_data_run()


@celery_app.task
def query_jira_data(project_id):
    project = get_object_or_404(Project, pk=project_id)
    jira_data = parse_jira_data(project.fetch_jira_data['issues'])

    try:
        result = project.resulthistory_set.latest('confirmed')
        if result.query_results == jira_data:
            result.confirmed = datetime.now()
            result.save()
        else:
            result = ResultHistory.objects.create(
                project=project,
                # confirmed=datetime.now(),
                query_results=jira_data,
            )
    except ResultHistory.DoesNotExist:
        result = ResultHistory.objects.create(
            project=project,
            # confirmed=datetime.now(),
            query_results=jira_data,
        )

