from datetime import date, datetime, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from ceeq.apps.calculator.tasks import calculate_score
from ceeq.apps.projects.models import ProjectComponentsDefectsDensity, FrameworkParameter

from ceeq.apps.queries.models import Project, ImpactMap
from ceeq.apps.calculator.models import ComponentImpact, LiveSettings
from ceeq.apps.queries.forms import ProjectForm, ProjectNewForm
from ceeq.apps.queries.tasks import fetch_jira_data_run
from ceeq.apps.queries.utils import get_impact_maps, get_instances
from ceeq.apps.users.views import user_is_superuser


@login_required
def projects(request):
    projects_active = Project.objects.filter(complete=False).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
    projects_archive = Project.objects.filter(complete=True).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
    project_dds = ProjectComponentsDefectsDensity.objects.all().order_by('project', 'version')
    framework_parameters = FrameworkParameter.objects.all()

    try:
        ls = LiveSettings.objects.all()[0]
        score_scalar = ls.score_scalar
    except LiveSettings.DoesNotExist:
        score_scalar = 10
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
        'dds': project_dds,
        'framework_parameters': framework_parameters,
        'framework_parameters_items': ['jira_issue_weight_sum',
                                       'vaf_ratio',
                                       'vaf_exp'],
        'superuser': request.user.is_superuser,
        'ceeq_components': sorted(ceeq_components.iteritems())

    })

    return render(request, 'q_projects/projects_start.html', context)


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    calculate_score(project.id)

    if project.complete and not request.user.is_superuser:
        messages.warning(request, 'The project \"{0}\" is archived.'.format(project.name))
        return redirect(projects)

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

    # jira_data = project.resulthistory_set.latest('confirmed')

    context = RequestContext(request, {
        'form': form,
        'project': project,
        'version_names': project.fetch_jira_versions,
        'impact_maps': get_impact_maps(),
        'instances': get_instances(),
        'superuser': request.user.is_superuser
    })
    return render(request, 'q_project_detail/project_detail.html', context)
    # return HttpResponse(project.fetch_jira_versions)


@user_passes_test(user_is_superuser)
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            return redirect(project_detail, project.id)
        else:
            messages.error(request, 'Correct erros in the form')
            context = RequestContext(request, {
                'form': form,
                'project': project,
                'superuser': request.user.is_superuser,
                'version_names': ['All Versions']
            })
            return render(request, 'q_project_detail/project_detail.html', context)
    else:
        return redirect(projects)


@user_passes_test(user_is_superuser)
def project_new(request):
    if request.method == 'POST':
        form = ProjectNewForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project \"{0}\" has been created.".format(project.name))
            return redirect(projects)
        else:
            messages.error(request, "Correct errors in the form.")
            context = RequestContext(request, {
                'form': form,
                'instances': get_instances(),
                'impact_maps': get_impact_maps()
            })
            return render(request, 'q_projects/project_new.html', context)
    else:
        form = ProjectNewForm()
        context = RequestContext(request, {
            'form': form,
            'instances': get_instances(),
            'impact_maps': get_impact_maps()
        })
        return render(request, 'q_projects/project_new.html', context)


@user_passes_test(user_is_superuser)
def project_delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Project \"{0}\" has been deleted.".format(project.name))

    return redirect(projects)


def project_archive(request, project_id):
    if request.method == 'GET':
        project = get_object_or_404(Project, pk=project_id)
        if project.complete:
            project.complete = False
        elif not project.complete:
            project.complete = True

        project.save()

    return redirect(projects)


def project_track(request, project_id):
    if request.method == 'GET':
        project = get_object_or_404(Project, pk=project_id)
        if project.active:
            project.active = False
        elif not project.active:
            project.active = True

        project.save()

    return redirect(projects)