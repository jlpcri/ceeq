from datetime import datetime
from celery import group
from django.shortcuts import get_object_or_404
from celery.schedules import crontab
from celery.task import PeriodicTask
from ceeq.apps.calculator.views import calculate_score_all
from ceeq.apps.usage.views import update_project_access_history

from ceeq.celery_module import app
from ceeq.apps.calculator.models import ResultHistory, LiveSettings, ComponentImpact
from ceeq.apps.queries.utils import parse_jira_data
from models import Project
from ceeq.apps.calculator.tasks import calculate_score


# class FetchJiraDataRun(PeriodicTask):
#     """
#     Fetch jira data from jira instance and update/create ResultHistory object
#     """
#
#     run_every = crontab(minute='*/10')
#
#     def run(self):
#         projects = Project.objects.filter(complete=False)
#         start = datetime.now()
#
#         if projects:
#             for project in projects:
#                 query_jira_data.delay(project.id)
#
#             current_delay = (datetime.now() - start).total_seconds()
#
#             try:
#                 ls = LiveSettings.objects.get(pk=1)
#                 ls.current_delay = current_delay
#                 ls.save()
#             except LiveSettings.DoesNotExist:
#                 LiveSettings.objects.create(score_scalar=20,
#                                             current_delay=current_delay)
#
#             return True
#         else:
#             return False


@app.task
def fetch_jira_data_run():
    """
    Fetch jira data from jira instance and update/create ResultHistory object
    """
    projects = Project.objects.filter(complete=False)
    start = datetime.now()
    # job = group(query_jira_data.delay(project.id) for project in projects)()

    for project in projects:
        query_jira_data.delay(project.id)

    current_delay = (datetime.now() - start).total_seconds()
    # print current_delay

    try:
        ls = LiveSettings.objects.get(pk=1)
        ls.current_delay = current_delay
        ls.save()
    except LiveSettings.DoesNotExist:
        LiveSettings.objects.create(score_scalar=20,
                                    current_delay=current_delay)

    # time.sleep(60)
    # fetch_jira_data_run.apply_async(countdown=60)

@app.task
def query_jira_data(project_id):
    project = get_object_or_404(Project, pk=project_id)
    component_impacts = ComponentImpact.objects.filter(impact_map=project.impact_map)
    component_names = []
    for impact in component_impacts:
        component_names.append(impact.component_name + '/')

    jira_data = parse_jira_data(project, component_names)
    today = datetime.today().date()

    try:
        result = project.resulthistory_set.latest('confirmed')
        if result.query_results == jira_data and result.created.date() == today:  # at least one record per day
            result.confirmed = datetime.now()
            result.save()
        else:
            result = ResultHistory.objects.create(
                project=project,
                query_results=jira_data,
            )
            calculate_score.delay(project.id)
    except ResultHistory.DoesNotExist:
        result = ResultHistory.objects.create(
            project=project,
            query_results=jira_data,
        )
        calculate_score.delay(project.id)


@app.task
def daily_score_log():
    calculate_score_all(None)
    update_project_access_history(None)
