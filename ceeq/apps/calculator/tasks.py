from django.shortcuts import get_object_or_404
from ceeq import celery_app

from ceeq.apps.calculator.models import ImpactMap, ComponentImpact, ComponentComplexity, ResultHistory, SeverityMap
from ceeq.apps.calculator.utils import get_table_data, get_score_data, get_score_by_component
from ceeq.apps.queries.models import Project


@celery_app.task
def calculate_score(project_id):
    project = get_object_or_404(Project, pk=project_id)
    result_latest = project.resulthistory_set.latest('confirmed')
    query_results = result_latest.query_results

    component_impacts = ComponentImpact.objects.filter(impact_map=project.impact_map)
    component_names = []
    for impact in component_impacts:
        component_names.append(impact.component_name)

    # internal_table = get_table_data(query_results, 'internal')
    # uat_table = get_table_data(query_results, 'uat')
    # combined_table = get_table_data(query_results, 'overall')

    internal_data = get_score_data(project, query_results, 'exclude_uat')
    uat_data = get_score_data(project, query_results, 'only_uat')
    overall_data = get_score_data(project, query_results, 'include_uat')

    # score_by_component = get_score_by_component(query_results, 'overall')

