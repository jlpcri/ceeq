from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from ceeq.apps.projects.models import ProjectComponentsDefectsDensity, FrameworkParameter, ProjectType, ProjectComponent

from ceeq.apps.queries.models import Project
from ceeq.apps.queries.forms import ProjectForm, ProjectNewForm
from ceeq.apps.users.views import user_is_superuser


@login_required
def projects(request):
    projects_active = Project.objects.filter(complete=False).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
    projects_archive = Project.objects.filter(complete=True).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
    project_dds = ProjectComponentsDefectsDensity.objects.all().order_by('project', 'version')
    framework_parameters = FrameworkParameter.objects.all()

    ceeq_components = {}
    for project_type in ProjectType.objects.all():
        temp_components = {}
        components = ProjectComponent.objects.filter(project_type=project_type)
        for component in components:
            temp_components[component.name] = Decimal(component.weight) / 20
        ceeq_components[project_type.name] = sorted(temp_components.iteritems())

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
    data = project.fetch_jira_versions

    return HttpResponse(data)


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
            })
            return render(request, 'q_projects/project_new.html', context)
    else:
        form = ProjectNewForm()
        context = RequestContext(request, {
            'form': form,
            'project_types': ''
        })
        return render(request, 'q_projects/project_new.html', context)
