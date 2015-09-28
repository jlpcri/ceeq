from datetime import datetime
from django.shortcuts import get_object_or_404
from django.utils.timezone import utc
from celery.schedules import crontab
from celery.task import PeriodicTask

from ceeq.celery_module import app
from ceeq.apps.calculator.models import ResultHistory, LiveSettings, ComponentImpact
from ceeq.apps.queries.utils import parse_jira_data
from models import Project


class FetchJiraDataRun(PeriodicTask):
    """
    Fetch jira data from jira instance and update/create ResultHistory object
    """

    run_every = crontab(minute='*/10')

    def run(self):
        projects = Project.objects.filter(complete=False)
        start = datetime.now()

        if projects:
            for project in projects:
                query_jira_data.delay(project.id)

            current_delay = (datetime.now() - start).total_seconds()

            try:
                ls = LiveSettings.objects.get(pk=1)
                ls.current_delay = current_delay
                ls.save()
            except LiveSettings.DoesNotExist:
                LiveSettings.objects.create(score_scalar=20,
                                            current_delay=current_delay)

            return True
        else:
            return False


@app.task
def query_jira_data(project_id):
    project = get_object_or_404(Project, pk=project_id)
    component_impacts = ComponentImpact.objects.filter(impact_map=project.impact_map)
    component_names = []
    for impact in component_impacts:
        component_names.append(impact.component_name + '/')

    jira_data = parse_jira_data(project, component_names)

    try:
        result = project.resulthistory_set.latest('confirmed')
        day_difference = datetime.utcnow().replace(tzinfo=utc).day - result.created.day
        if result.query_results == jira_data and day_difference == 0:  # at least one record per day
            result.confirmed = datetime.now()
            result.save()
        else:
            result = ResultHistory.objects.create(
                project=project,
                query_results=jira_data,
            )
    except ResultHistory.DoesNotExist:
        result = ResultHistory.objects.create(
            project=project,
            query_results=jira_data,
        )

