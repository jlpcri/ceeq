from datetime import date, datetime, timedelta
import time
from decimal import Decimal
import json
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from ceeq.apps.calculator.utils import get_score_data

from ceeq.apps.queries.models import Project, ImpactMap, ScoreHistory
from ceeq.apps.calculator.models import ComponentImpact, LiveSettings, ResultHistory
from ceeq.apps.queries.forms import ProjectForm, ProjectNewForm
from ceeq.apps.queries.tasks import query_jira_data
from ceeq.apps.queries.utils import get_impact_maps, get_instances
from ceeq.apps.users.views import user_is_superuser


@login_required
def projects(request):
    projects_active = Project.objects.filter(complete=False).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
    projects_archive = Project.objects.filter(complete=True).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')

    try:
        ls = LiveSettings.objects.all()[0]
        score_scalar = ls.score_scalar
    except (LiveSettings.DoesNotExist, IndexError):
        score_scalar = 20
    ceeq_components = {}
    for impact_map in ImpactMap.objects.all():
        temp_components = {}
        components = ComponentImpact.objects.filter(impact_map=impact_map)
        for component in components:
            temp_components[component.component_name] = Decimal(component.impact) / score_scalar
        ceeq_components[impact_map.name] = sorted(temp_components.iteritems())

    context = RequestContext(request, {
        'projects_active': projects_active,
        'projects_archive': projects_archive,
        'framework_parameters_items': ['jira_issue_weight_sum',
                                       'vaf_ratio',
                                       'vaf_exp'],
        'superuser': request.user.is_superuser,
        'ceeq_components': sorted(ceeq_components.iteritems())

    })
    return render(request, 'queries/projects/projects_start.html', context)


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # update ScoreHistory for Access field
    update_access_history(project.id)

    if project.complete and not request.user.is_superuser:
        messages.warning(request, 'The project \"{0}\" is archived.'.format(project.name))
        return HttpResponseRedirect(reverse('queries:projects'))

    form = ProjectForm(instance=project)

    # Filter query results for input created date range
    try:
        end = date.fromtimestamp(float(request.GET.get('end')))
    except (TypeError, ValueError):
        end = datetime.now().date()

    try:
        start = date.fromtimestamp(float(request.GET.get('start')))
    except (TypeError, ValueError):
        start = end - timedelta(days=29)

    uat_type_custom = request.GET.get('uat_type_custom', 'exclude_uat')
    last_tab = request.GET.get('last_tab', '')

    # get standard component names
    component_impacts = ComponentImpact.objects.filter(impact_map=project.impact_map)
    component_names_standard = []
    for impact in component_impacts:
        component_names_standard.append(impact.component_name)

    try:
        result_latest = project.resulthistory_set.latest('confirmed')
    except ResultHistory.DoesNotExist:
        query_jira_data(project.id)
        result_latest = project.resulthistory_set.latest('confirmed')



    # Calculate weight factor, exist components etc.
    query_results = result_latest.query_results

    # get custom data from query results
    query_results_custom = []
    for item in query_results:
        if start.strftime("%Y-%m-%d") <= item['created'] <= (end + timedelta(days=1)).strftime("%Y-%m-%d"):
            query_results_custom.append(item)

    internal_data = get_score_data(project, query_results, 'exclude_uat')
    uat_data = get_score_data(project, query_results, 'only_uat')
    overall_data = get_score_data(project, query_results, 'include_uat')
    custom_data = get_score_data(project, query_results_custom, uat_type_custom)

    context = RequestContext(request, {
        'form': form,
        'project': project,
        'version_names': project.fetch_jira_versions,
        'impact_maps': get_impact_maps(),
        'instances': get_instances(),
        'superuser': request.user.is_superuser,

        'start': float(request.GET.get('start', time.mktime(start.timetuple()))),
        'end': time.mktime(end.timetuple()),
        'uat_type_custom': uat_type_custom,
        'last_tab': last_tab,

        'weight_factor_include_uat': overall_data['weight_factor'],
        'weight_factor_exclude_uat': internal_data['weight_factor'],
        'weight_factor_only_uat': uat_data['weight_factor'],
        'weight_factor_custom': custom_data['weight_factor'],

        'component_names_standard': component_names_standard,
        'component_names_include_uat': overall_data['components_exist'],
        'component_names_exclude_uat': internal_data['components_exist'],
        'component_names_only_uat': uat_data['components_exist'],
        'component_names_custom': custom_data['components_exist'],

        'priority_total_include_uat': overall_data['priority_total'],
        'priority_total_exclude_uat': internal_data['priority_total'],
        'priority_total_only_uat': uat_data['priority_total'],
        'priority_total_custom': custom_data['priority_total'],

        'dd_pie_data_include_uat': json.dumps(overall_data['pie_chart_data']),
        'dd_pie_data_exclude_uat': json.dumps(internal_data['pie_chart_data']),
        'dd_pie_data_only_uat': json.dumps(uat_data['pie_chart_data']),
        'dd_pie_data_custom': json.dumps(custom_data['pie_chart_data']),

        'overall_score': overall_data['score'][0],
        'internal_score': internal_data['score'][0],
        'uat_score': uat_data['score'][0],
        'custom_score': custom_data['score'][0],

        'ceeq_trend_graph_include_uat': overall_data['ceeq_trend_graph'],
        'ceeq_trend_graph_exclude_uat': internal_data['ceeq_trend_graph'],

    })
    return render(request, 'queries/project_detail/project_detail.html', context)


@user_passes_test(user_is_superuser)
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            query_jira_data(project.id)
            return HttpResponseRedirect(reverse('queries:project_detail',
                                                kwargs={'project_id': project.id}))
        else:
            messages.error(request, 'Correct erros in the form')
            context = RequestContext(request, {
                'form': form,
                'project': project,
                'superuser': request.user.is_superuser,
                'version_names': ['All Versions']
            })
            return render(request, 'queries/project_detail/project_detail.html', context)
    else:
        return HttpResponseRedirect(reverse('queries:projects'))


@user_passes_test(user_is_superuser)
def project_new(request):
    if request.method == 'POST':
        form = ProjectNewForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project \"{0}\" has been created.".format(project.name))
            return HttpResponseRedirect(reverse('queries:projects'))
        else:
            messages.error(request, "Correct errors in the form.")
            context = RequestContext(request, {
                'form': form,
                'instances': get_instances(),
                'impact_maps': get_impact_maps()
            })
            return render(request, 'queries/projects/project_new.html', context)
    else:
        form = ProjectNewForm()
        context = RequestContext(request, {
            'form': form,
            'instances': get_instances(),
            'impact_maps': get_impact_maps()
        })
        return render(request, 'queries/projects/project_new.html', context)


@user_passes_test(user_is_superuser)
def project_delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Project \"{0}\" has been deleted.".format(project.name))

    return HttpResponseRedirect(reverse('queries:projects'))


def project_archive(request, project_id):
    if request.method == 'GET':
        project = get_object_or_404(Project, pk=project_id)
        if project.complete:
            project.complete = False
        elif not project.complete:
            project.complete = True

        project.save()

    return HttpResponseRedirect(reverse('queries:projects'))


def project_track(request, project_id):
    if request.method == 'GET':
        project = get_object_or_404(Project, pk=project_id)
        if project.active:
            project.active = False
        elif not project.active:
            project.active = True

        project.save()

    return HttpResponseRedirect(reverse('queries:projects'))


def query_jira_data_all(request):
    ps = Project.objects.filter(complete=False)
    for project in ps:
        query_jira_data.delay(project.id)

    # query_jira_data(8)
    return HttpResponseRedirect(reverse('queries:projects'))


def fetch_projects_score(request):
    """
    Use for ceeq score bar graph
    :param request:
    :return: json data
            categories: Y axis label
            score: X axis value
            id: project id for hyperlink of project detail
    """
    projects = Project.objects.filter(complete=False).extra(select={'lower_name': 'lower(jira_key)'}).order_by('lower_name')
    data = {}

    data['categories'] = [project.jira_key.upper() + '-' + project.jira_version for project in projects]
    data['score'] = []
    for project in projects:
        score = project.internal_score
        if score < 10:
            data['score'].append(str(score))
        elif score == 103:
            data['score'].append(str(10.00))
        else:
            data['score'].append(str(0))
    data['id'] = [str(project.id) for project in projects]

    return HttpResponse(json.dumps(data), content_type="application/json")


def update_access_history(project_id):
    """
    Update Project Access per project
    :param project_id:
    :return:
    """
    project = get_object_or_404(Project, pk=project_id)
    today = datetime.today().date()
    try:
        access = project.scorehistory_set.latest('created')
        if access.created.date() == today:
            if not access.access:
                access.access = True
                access.save()
        else:
            access = ScoreHistory.objects.create(project=project)
            access.access = True
            access.save()
    except ScoreHistory.DoesNotExist:
        access = ScoreHistory.objects.create(project=project)
        access.access = True
        access.save()
