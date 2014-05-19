from decimal import Decimal
import json
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
import requests
from collections import OrderedDict
from django.contrib.auth.decorators import login_required, user_passes_test
from ceeq.apps.users.views import user_is_superuser

from models import Project, ProjectComponentsWeight
from forms import ProjectForm


def projects(request):
    projects = Project.objects.all().order_by('name')
    context = RequestContext(request, {
        'projects': projects,
    })
    return render(request, 'projects_start.html', context)

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    component_weight_list = ProjectComponentsWeight.objects.filter(project=project)
    weight_sum = 0
    for component_weight in component_weight_list:
        weight_sum += component_weight.weight
    weight_left = 1 - weight_sum

    # Get component names for autocomplete
    component_names = []
    jira_data = fetch_jira_data(project.jira_name)
    for item in jira_data['issues']:
        try:
            name = str(item['fields']['components'][0]['name'])
            component_names.append(truncate_after_slash(name))
        except IndexError:
            continue
    component_names = list(OrderedDict.fromkeys(component_names))
    component_names = sorted(component_names)

    form = ProjectForm(instance=project)

    context = RequestContext(request, {
        'form': form,
        'project': project,
        'weight_left': weight_left,
        'component_names': component_names,
        'superuser': request.user.is_superuser,
    })
    return render(request, 'project_detail.html', context)


def truncate_after_slash(string):
    if '/' in string:
        index = string.index('/')
        return string[:index]
    else:
        return string


@user_passes_test(user_is_superuser)
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Projects info has been saved.")
            return redirect(projects)
        else:
            messages.error(request, "Correct errors in the form.")
            context = RequestContext(request, {
                'form': form,
                'project': project,
            })
            return render(request, 'project_detail.html', context)
    else:
        return redirect(projects)

@user_passes_test(user_is_superuser)
def project_new(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project \"{0}\" has been created.".format(project.name))
            return redirect(projects)
        else:
            messages.error(request, "Correct errors in the form.")
            context = RequestContext(request, {
                'form': form,
            })
            return render(request, 'project_new.html', context)
    else:
        form = ProjectForm()
        context = RequestContext(request, {
            'form': form,
        })
        return render(request, 'project_new.html', context)

@user_passes_test(user_is_superuser)
def project_delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Project \"{0}\" has been deleted.".format(project.name))

    return redirect(reverse('projects.apps.projects.views.projects'))

@login_required
def project_update_scores(request, project_id):
    projects = Project.objects.all().order_by('name')
    if project_id == '1000000':
        for project in projects:
            jira_data = fetch_jira_data(project.jira_name)
            calculate_score(project, jira_data)
    else:
        project = get_object_or_404(Project, pk=project_id)
        jira_data = fetch_jira_data(project.jira_name)
        calculate_score(project, jira_data)

    context = RequestContext(request, {
        'projects': projects,
    })
    return render(request, 'projects_start.html', context)


def fetch_jira_data(jira_name):
    url = 'http://jira.west.com/rest/api/2/search?fields=components,status,priority&jql=project=' + jira_name
    data = requests.get(url, auth=('sliu', 'Sissy981129')).json()
    return data


def calculate_score(project, jira_data):
    # Get component names for autocomplete
    component_names = []
    component_names_without_slash = []
    jira_data = fetch_jira_data(project.jira_name)
    for item in jira_data['issues']:
        try:
            name = str(item['fields']['components'][0]['name'])
            component_names.append(name)
            component_names_without_slash.append(truncate_after_slash(name))
        except IndexError:
            continue
    component_names = list(OrderedDict.fromkeys(component_names))
    component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

    # Construct # of different priority issues dict from jira_data
    data = {}
    issue_counts = {
        'total': 0,
        'blocker': 0,
        'critical': 0,
        'major': 0,
        'minor': 0,
        'trivial': 0
    }
    for item in component_names:
        data[item] = issue_counts.copy()  # copy the dict object

    for item in component_names_without_slash: # add component item to data
        if item in data.keys():
            continue
        else:
            data[item] = issue_counts.copy()

    for item in jira_data['issues']:
        try:
            component = item['fields']['components'][0]['name']
            if (item['fields']['status']['id'] in ['1', '4']):  # 1-open, 4-reopen
                if item['fields']['priority']['id'] == '1':
                    data[component]['blocker'] += 1
                elif item['fields']['priority']['id'] == '2':
                    data[component]['critical'] += 1
                elif item['fields']['priority']['id'] == '3':
                    data[component]['major'] += 1
                elif item['fields']['priority']['id'] == '4':
                    data[component]['minor'] += 1
                elif item['fields']['priority']['id'] == '5':
                    data[component]['trivial'] += 1
        except IndexError:
            continue

    # Weight: Blocker-1.08, Critical-0.84, Major-0.60, Minor-0.36, Trivial-0.12, Total-3.00
    for item in data:
        data[item]['blocker'] *= 1.08
        data[item]['critical'] *= 0.84
        data[item]['major'] *= 0.60
        data[item]['minor'] *= 0.36
        data[item]['trivial'] *= 0.12

    for item in data:
        data[item]['total'] = data[item]['blocker']\
                              + data[item]['critical']\
                              + data[item]['major']\
                              + data[item]['minor']\
                              + data[item]['trivial']

    # Formalize each component from its sub-component
    for component in component_names_without_slash:
        subcomponent_length = 0
        subcomponent_total = 0
        for item in data:
            if item.startswith(component+'/'):
                subcomponent_length +=1
                subcomponent_total += data[item]['total']
            else:
                continue

        #print subcomponent_length, subcomponent_total
        if subcomponent_length == 0:
            continue
        else:
            data[component]['total'] = subcomponent_total / subcomponent_length


    weight_list = ProjectComponentsWeight.objects.filter(project=project)
    if weight_list.count() == 0:
        project.score = -1
        project.save()
        return
    weight_dict = {}
    for item in weight_list:
        weight_dict[item.component] = {
            'weight': item.weight,
            'count': item.count
        }

    for key in weight_dict.keys():
        if key in data.keys():
            weight_dict[key]['count'] = weight_dict[key]['weight'] * Decimal(data[key]['total'])

    # Calculate Raw Score of project
    raw_score = 0
    for item in weight_dict:
        raw_score += weight_dict[item]['count']

    #print round(raw_score, 2)

    #Calculate VAF(Value Adjustment Factor)
    test_character = project.accuracy + project.suitability + project.interoperability \
    + project.functional_security + project.usability + project.accessibility \
    + project.technical_security + project.reliability + project.efficiency \
    + project.maintainability + project.portability

    vaf = 0.01 * test_character + 0.65   # VAF value
    score =10 - raw_score / Decimal(vaf) # projects score = 10 - defect score

    if score > 10 or score < 0: # projects score out of range (0-10)
        project.score = -1
    else:
        project.score = round(score, 2)
    project.save()


def fetch_projects_score(request):
    projects = Project.objects.all()
    data = {}

    data['categories'] = [project.name for project in projects]
    data['score'] = [str(project.score) for project in projects]

    return HttpResponse(json.dumps(data), content_type="application/json")