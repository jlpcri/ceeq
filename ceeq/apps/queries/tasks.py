from datetime import datetime
import time
from django.shortcuts import get_object_or_404
from celery import group

from ceeq import celery_app
from ceeq.apps.calculator.models import ResultHistory, LiveSettings, ComponentImpact
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
    job = group(query_jira_data.delay(project.id) for project in projects)
    job_result = job.apply_async()

    # while True:
    #     if job_result.successful():
    #         print 'done'
    #         end = datetime.now()
    #         current_delay = int((end - start).total_seconds())
    #         break
    #     print 'running'
    #
    # print current_delay

    try:
        ls = LiveSettings.objects.get(pk=1)
        ls.current_delay = current_delay
        ls.save()
    except LiveSettings.DoesNotExist:
        LiveSettings.objects.create(score_scalar=20,
                                    current_delay=current_delay)

    time.sleep(10)
    # fetch_jira_data_run()


@celery_app.task
def query_jira_data(project_id):
    project = get_object_or_404(Project, pk=project_id)
    component_impacts = ComponentImpact.objects.filter(impact_map=project.impact_map)
    component_names = []
    for impact in component_impacts:
        component_names.append(impact.component_name + '/')

    jira_data = parse_jira_data(project.fetch_jira_data['issues'], component_names)

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

