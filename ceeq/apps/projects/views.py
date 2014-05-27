from decimal import Decimal
import json
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
import requests
from collections import OrderedDict
from django.contrib.auth.decorators import login_required, user_passes_test
from ceeq.apps.users.views import user_is_superuser

from models import Project, ProjectComponentsWeight, FrameworkParameter
from forms import ProjectForm


def projects(request):
    projects = Project.objects.all().order_by('name')
    framework_parameters = FrameworkParameter.objects.all()
    context = RequestContext(request, {
        'projects': projects,
        'framework_parameters': framework_parameters,
        'framework_parameters_items': ['jira_issue_weight_sum',
                                       'vaf_ratio',
                                       'vaf_exp']
    })
    return render(request, 'projects_start.html', context)

# pre-define Standard Component Name and its comparison ratio
component_names_standard = {'CDR Feeds': 2,
                            'CXP': 2,
                            'Outbound': 1,
                            'Platform': 3,
                            'Reports': 4,
                            'Voice Apps': 8
                            }

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    #component_weight_list = ProjectComponentsWeight.objects.filter(project=project)
    #weight_sum = 0
    #for component_weight in component_weight_list:
    #    weight_sum += component_weight.weight
    #weight_left = 1 - weight_sum

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
    #component_names = sorted(component_names)

    weight_factor = []
    weight_factor_base = 0
    for item in component_names:
        try:
            weight_factor_base += component_names_standard[item]
        except KeyError:
            continue

    for item in component_names:
        temp = []
        temp.append(item)
        temp.append(round(component_names_standard[item] / float(weight_factor_base), 2))
        weight_factor.append(temp)
    #print sorted(weight_factor)

    form = ProjectForm(instance=project)

    context = RequestContext(request, {
        'form': form,
        'project': project,
        'weight_factor': sorted(weight_factor),
        'component_names_standard': sorted(component_names_standard.keys()),
        'component_names': sorted([item for item in component_names_standard.keys() if item in component_names]),
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

    return redirect(reverse('ceeq.apps.projects.views.projects'))

@login_required
def project_update_scores(request, project_id):
    projects = Project.objects.all().order_by('name')
    if project_id == '1000000':
        for project in projects:
            calculate_score(project)
    else:
        project = get_object_or_404(Project, pk=project_id)
        calculate_score(project)

    context = RequestContext(request, {
        'projects': projects,
    })
    return render(request, 'projects_start.html', context)


def fetch_jira_data(jira_name):
    url = 'http://jira.west.com/rest/api/2/search?fields=components,status,priority&jql=project=' + jira_name
    data = requests.get(url, auth=('sliu', 'Sissy981129')).json()
    return data


def calculate_score(project):
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

    #print component_names_without_slash
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

    #get framework parameter
    parameter = {}
    framework_parameters = FrameworkParameter.objects.all()
    for framework_parameter in framework_parameters:
        parameter[framework_parameter.parameter] = framework_parameter.value

    try:
        jira_issue_weight_sum = parameter['jira_issue_weight_sum']
    except KeyError:
        jira_issue_weight_sum = Decimal(3.00)
    try:
        vaf_ratio = parameter['vaf_ratio']
    except KeyError:
        vaf_ratio = Decimal(0.01)
    try:
        vaf_exp = parameter['vaf_exp']
    except KeyError:
        vaf_exp = Decimal(0.65)

    # Weight: Blocker-9/25, Critical-7/25, Major-5/25, Minor-3/25, Trivial-1/25, Total-25/25 * sum
    for item in data:
        data[item]['blocker'] *= jira_issue_weight_sum * 9 / 25
        data[item]['critical'] *= jira_issue_weight_sum * 7 / 25
        data[item]['major'] *= jira_issue_weight_sum * 5 / 25
        data[item]['minor'] *= jira_issue_weight_sum * 3 / 25
        data[item]['trivial'] *= jira_issue_weight_sum * 1 / 25

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

    #weight_list = ProjectComponentsWeight.objects.filter(project=project)
    #If no component weight input then return
    if len(component_names_without_slash) == 0:
        project.score = -1
        project.save()
        return

    weight_dict = {}

    #calculate total component weighted factor base
    weight_factor_base = 0
    for item in component_names_without_slash:
        try:
            weight_factor_base += component_names_standard[item]
        except KeyError:
            continue

    #print component_names_without_slash

    for item in component_names_without_slash:
        weight_dict[item] = {
            'weight': round(component_names_standard[item] / float(weight_factor_base), 2),
            'count': 0
        }

    for key in weight_dict.keys():
        if key in data.keys():
            weight_dict[key]['count'] = Decimal(weight_dict[key]['weight']) * Decimal(data[key]['total'])

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

    vaf = vaf_ratio * test_character + vaf_exp   # VAF value
    score =10 - raw_score / Decimal(vaf)  # projects score = 10 - defect score

    if score > 10 or score < 0:  # projects score out of range (0-10)
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