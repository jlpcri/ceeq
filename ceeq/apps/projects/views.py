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

from models import Project, FrameworkParameter
from forms import ProjectForm


def projects(request):
    projects = Project.objects.all().order_by('name')
    framework_parameters = FrameworkParameter.objects.all()
    context = RequestContext(request, {
        'projects': projects,
        'framework_parameters': framework_parameters,
        'framework_parameters_items': ['jira_issue_weight_sum',
                                       'vaf_ratio',
                                       'vaf_exp'],
        'superuser': request.user.is_superuser

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
    form = ProjectForm(instance=project)

    component_names = []
    component_names_without_slash = []
    version_names = []

    jira_data = fetch_jira_data(project.jira_name)

    #check whether fetch the data from jira or not

    if jira_data == 'No JIRA Data':
        messages.warning(request, 'The project \"{0}\" does not exist in JIRA'.format(project.jira_name))
        context = RequestContext(request, {
        'form': form,
        'project': project,
        'superuser': request.user.is_superuser,
        'no_jira_data': jira_data,
        })
        return render(request, 'project_detail.html', context)

    for item in jira_data['issues']:
        try:
            name = str(item['fields']['components'][0]['name'])
            component_names.append(name)
            component_names_without_slash.append(truncate_after_slash(name))
        except IndexError:
            continue
    component_names = list(OrderedDict.fromkeys(component_names))
    component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

    data = issue_counts_compute(component_names, component_names_without_slash, jira_data['issues'])

    #calculate issues number of components and sub-components
    for component in component_names_without_slash:
        for item in data:
            if item.startswith(component+'/'):
                data[item]['total'] = data[item]['blocker'] \
                                    + data[item]['critical'] \
                                    + data[item]['major'] \
                                    + data[item]['minor'] \
                                    + data[item]['trivial']
                data[component]['blocker'] += data[item]['blocker']
                data[component]['critical'] += data[item]['critical']
                data[component]['major'] += data[item]['major']
                data[component]['minor'] += data[item]['minor']
                data[component]['trivial'] += data[item]['trivial']

    #get jira issue weight sum value
    try:
        jira_issue_weight_sum = FrameworkParameter.objects.get(parameter='jira_issue_weight_sum').value
    except KeyError:
        jira_issue_weight_sum = Decimal(3.00)

    #calculate defect density of each component
    for item in component_names_without_slash:
        data[item]['total'] = data[item]['blocker'] * jira_issue_weight_sum * 9 / 25 \
                              + data[item]['critical'] * jira_issue_weight_sum * 7 / 25 \
                              + data[item]['major'] * jira_issue_weight_sum * 5 / 25 \
                              + data[item]['minor'] * jira_issue_weight_sum * 3 / 25 \
                              + data[item]['trivial'] * jira_issue_weight_sum * 1 / 25

    #formalize total sum of each component by divided by number of sub-components
    for component in component_names_without_slash:
        subcomponent_length = 0
        for item in data:
            #if sub component has zero issue then skip
            if item.startswith(component+'/') and data[item]['total'] > 0:
                subcomponent_length += 1
            else:
                continue
        if subcomponent_length == 0:
            continue
        else:
            data[component]['total'] /= subcomponent_length

    weight_factor = []
    weight_factor_base = 0
    for item in component_names_without_slash:
        try:
            weight_factor_base += component_names_standard[item]
        except KeyError:
            continue

    for item in component_names_without_slash:
        temp = []
        temp.append(item)
        try:
            temp.append(round(component_names_standard[item] / float(weight_factor_base), 3))
        except KeyError:
            continue
        temp.append(data[item]['total'])
        temp.append(data[item]['blocker'] \
                    + data[item]['critical'] \
                    + data[item]['major'] \
                    + data[item]['minor'] \
                    + data[item]['trivial'])
        temp.append(data[item]['blocker'])
        temp.append(data[item]['critical'])
        temp.append(data[item]['major'])
        temp.append(data[item]['minor'])
        temp.append(data[item]['trivial'])
        weight_factor.append(temp)

    context = RequestContext(request, {
        'form': form,
        'project': project,
        'weight_factor': sorted(weight_factor),
        'component_names_standard': sorted(component_names_standard.keys()),
        'component_names': sorted([item for item in component_names_standard.keys() if item in component_names_without_slash]),
        'superuser': request.user.is_superuser,
    })
    return render(request, 'project_detail.html', context)


def project_defects_density(request, project_id):
    project = get_object_or_404(Project, pk=project_id)


    version_names = []

    jira_data = fetch_jira_data(project.jira_name)

    #check whether fetch the data from jira or not

    if jira_data == 'No JIRA Data':
        messages.warning(request, 'The project \"{0}\" does not exist in JIRA'.format(project.jira_name))
        context = RequestContext(request, {
        'project': project,
        'superuser': request.user.is_superuser,
        'no_jira_data': jira_data,
        })
        return render(request, 'project_dd_detail.html', context)

    #print jira_data['issues']

    #print '------------------------------------'

    for item in jira_data['issues']:
        try:
            name = str(item['fields']['versions'][0]['name'])
            version_names.append(name)
        except IndexError:
            continue
    version_names = list(OrderedDict.fromkeys(version_names))

    version_data = {}
    for version_name in version_names:
        temp_data = []
        for item in jira_data['issues']:
            try:
                name = str(item['fields']['versions'][0]['name'])
                if name == version_name:
                    temp_data.append(item)
            except IndexError:
                continue
        version_data[version_name] = temp_data

    weight_factor_versions = {}
    for key in version_data.keys():
        component_names = []
        component_names_without_slash = []

        #get jira issue weight sum value
        try:
            jira_issue_weight_sum = FrameworkParameter.objects.get(parameter='jira_issue_weight_sum').value
        except KeyError:
            jira_issue_weight_sum = Decimal(3.00)

        for item in version_data[key]:
            try:
                name = str(item['fields']['components'][0]['name'])
                component_names.append(name)
                component_names_without_slash.append(truncate_after_slash(name))
            except IndexError:
                continue
        component_names = list(OrderedDict.fromkeys(component_names))
        component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

        data = issue_counts_compute(component_names, component_names_without_slash, version_data[key])

        #calculate issues number of components and sub-components
        for component in component_names_without_slash:
            for item in data:
                if item.startswith(component+'/'):
                    data[item]['total'] = data[item]['blocker'] \
                                        + data[item]['critical'] \
                                        + data[item]['major'] \
                                        + data[item]['minor'] \
                                        + data[item]['trivial']
                    data[component]['blocker'] += data[item]['blocker']
                    data[component]['critical'] += data[item]['critical']
                    data[component]['major'] += data[item]['major']
                    data[component]['minor'] += data[item]['minor']
                    data[component]['trivial'] += data[item]['trivial']

        #calculate defect density of each component
        for item in component_names_without_slash:
            data[item]['total'] = data[item]['blocker'] * jira_issue_weight_sum * 9 / 25 \
                                  + data[item]['critical'] * jira_issue_weight_sum * 7 / 25 \
                                  + data[item]['major'] * jira_issue_weight_sum * 5 / 25 \
                                  + data[item]['minor'] * jira_issue_weight_sum * 3 / 25 \
                                  + data[item]['trivial'] * jira_issue_weight_sum * 1 / 25

        #formalize total sum of each component by divided by number of sub-components
        for component in component_names_without_slash:
            subcomponent_length = 0
            for item in data:
                #if sub component has zero issue then skip
                if item.startswith(component+'/') and data[item]['total'] > 0:
                    subcomponent_length += 1
                else:
                    continue
            if subcomponent_length == 0:
                continue
            else:
                data[component]['total'] /= subcomponent_length

        weight_factor = []
        weight_factor_base = 0
        for item in component_names_without_slash:
            try:
                weight_factor_base += component_names_standard[item]
            except KeyError:
                continue

        for item in component_names_without_slash:
            temp = []
            temp.append(item)
            try:
                temp.append(round(component_names_standard[item] / float(weight_factor_base), 3))
            except KeyError:
                continue
            temp.append(data[item]['total'])
            temp.append(data[item]['blocker'] \
                        + data[item]['critical'] \
                        + data[item]['major'] \
                        + data[item]['minor'] \
                        + data[item]['trivial'])
            temp.append(data[item]['blocker'])
            temp.append(data[item]['critical'])
            temp.append(data[item]['major'])
            temp.append(data[item]['minor'])
            temp.append(data[item]['trivial'])
            weight_factor.append(temp)

        weight_factor_versions[key] = weight_factor

    context = RequestContext(request, {
        'project': project,
        'weight_factor_versions': weight_factor_versions,
        'component_names_standard': sorted(component_names_standard.keys()),
        'superuser': request.user.is_superuser
    })
    return render(request, 'projects_dd_start.html', context)


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
    framework_parameters = FrameworkParameter.objects.all()
    if project_id == '1000000':
        for project in projects:
            calculate_score(project)
    else:
        project = get_object_or_404(Project, pk=project_id)
        calculate_score(project)

    context = RequestContext(request, {
        'projects': projects,
        'framework_parameters': framework_parameters,
        'superuser': request.user.is_superuser
    })
    return render(request, 'projects_start.html', context)


def fetch_jira_data(jira_name):
    url = 'http://jira.west.com/rest/api/2/search?fields=components,status,priority,versions&jql=project=' + jira_name
    data = requests.get(url, auth=('sliu', 'Sissy981129')).json()
    if len(data) == 2:
        if data['errorMessages']:
            return 'No JIRA Data'
    else:
        return data


def calculate_score(project):
    # Get component names for autocomplete
    component_names = []
    component_names_without_slash = []
    jira_data = fetch_jira_data(project.jira_name)

    if jira_data == 'No JIRA Data':
        project.score = -4
        project.save()
        return

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
    data = issue_counts_compute(component_names, component_names_without_slash, jira_data['issues'])

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

    #calculate issues number of components and sub-components
    for component in component_names_without_slash:
        for item in data:
            if item.startswith(component+'/'):
                data[item]['total'] = data[item]['blocker'] \
                                    + data[item]['critical'] \
                                    + data[item]['major'] \
                                    + data[item]['minor'] \
                                    + data[item]['trivial']
                data[component]['blocker'] += data[item]['blocker']
                data[component]['critical'] += data[item]['critical']
                data[component]['major'] += data[item]['major']
                data[component]['minor'] += data[item]['minor']
                data[component]['trivial'] += data[item]['trivial']

    #calculate defect density of each component
    for item in component_names_without_slash:
        data[item]['total'] = data[item]['blocker'] * jira_issue_weight_sum * 9 / 25 \
                              + data[item]['critical'] * jira_issue_weight_sum * 7 / 25 \
                              + data[item]['major'] * jira_issue_weight_sum * 5 / 25 \
                              + data[item]['minor'] * jira_issue_weight_sum * 3 / 25 \
                              + data[item]['trivial'] * jira_issue_weight_sum * 1 / 25

    # Formalize each component from its sub-component
    for component in component_names_without_slash:
        subcomponent_length = 0
        for item in data:
            #if sub-component has zero issue then skip
            if item.startswith(component+'/') and data[item]['total'] > 0:
                subcomponent_length += 1
            else:
                continue

        if subcomponent_length == 0:
            continue
        else:
            data[component]['total'] /= subcomponent_length

    #If no component weight input then return
    if len(component_names_without_slash) == 0:  # non issue created in JIRA
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
        try:
            weight = round(component_names_standard[item] / float(weight_factor_base), 3)
        except KeyError:
            continue
        weight_dict[item] = {
            'weight': weight,
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
    score = 10 - raw_score / Decimal(vaf)  # projects score = 10 - defect score

    if score < 0:  # projects score out of range (0-10)
        project.score = -2
    elif score == 10:  # no open issues in JIRA
        project.score = -3
    else:
        project.score = round(score, 2)
    project.save()


def issue_counts_compute(component_names, component_names_without_slash, jira_data):
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

    for item in jira_data:
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

    return data


def fetch_projects_score(request):
    projects = Project.objects.all()
    data = {}

    data['categories'] = [project.name for project in projects]
    data['score'] = [str(project.score) for project in projects]

    return HttpResponse(json.dumps(data), content_type="application/json")