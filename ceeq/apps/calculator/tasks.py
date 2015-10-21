from django.shortcuts import get_object_or_404
from celery.schedules import crontab
from celery.task import PeriodicTask

from ceeq.celery_module import app
from ceeq.apps.calculator.utils import get_score_data, get_score_by_component, update_score_history
from ceeq.apps.queries.models import Project

"""
# no need running PeroidicTask for calculate_score, run calculate_score after query set is updated
class CalculateProjectScore(PeriodicTask):
    run_every = crontab(minute='*/9')

    def run(self):
        projects = Project.objects.filter(complete=False)

        if projects:
            for project in projects:
                calculate_score.delay(project.id)

            return True
        else:
            return False
"""


@app.task
def calculate_score(project_id):
    project = get_object_or_404(Project, pk=project_id)
    result_latest = project.resulthistory_set.latest('confirmed')
    query_results = result_latest.query_results

    internal_data = get_score_data(project, query_results, 'exclude_uat')
    uat_data = get_score_data(project, query_results, 'only_uat')
    overall_data = get_score_data(project, query_results, 'include_uat')

    result_latest.overall_score = overall_data['score'][0]
    result_latest.internal_score = internal_data['score'][0]
    result_latest.uat_score = uat_data['score'][0]

    result_latest.combined_testing_table = overall_data['score']
    result_latest.internal_testing_table = internal_data['score']
    result_latest.uat_testing_table = uat_data['score']

    result_latest.save()

    # update CEEQ score to ScoreHistory
    update_score_history(project.id,
                         overall_data['score'],
                         internal_data['score'],
                         uat_data['score'])

    # score_by_component = get_score_by_component(query_results, 'overall')

