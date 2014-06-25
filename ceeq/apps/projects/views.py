from datetime import date
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

from models import Project, FrameworkParameter, ProjectComponentsDefectsDensity
from forms import ProjectForm


def projects(request):
    projects = Project.objects.all().order_by('name')
    project_dds = ProjectComponentsDefectsDensity.objects.all().order_by('project', 'version')
    framework_parameters = FrameworkParameter.objects.all()
    context = RequestContext(request, {
        'projects': projects,
        'dds': project_dds,
        'framework_parameters': framework_parameters,
        'framework_parameters_items': ['jira_issue_weight_sum',
                                       'vaf_ratio',
                                       'vaf_exp'],
        'superuser': request.user.is_superuser

    })
    return render(request, 'projects_start.html', context)

# pre-define Standard Component Name and its comparison ratio
component_names_standard = {'CXP': 2,
                            'Platform': 4,
                            'Reports': 3,
                            'Application': 8,
                            'Voice Slots': 3,
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

    data = issue_counts_compute(request, component_names, component_names_without_slash, jira_data['issues'])

    weight_factor = get_component_defects_density_all(data,
                                                      component_names_without_slash)

    # calculate total number of issues based on priority
    priority_total = {
        'total': 0,
        'blocker': 0,
        'critical': 0,
        'major': 0,
        'minor': 0,
        'trivial': 0
    }
    for item in weight_factor:
        priority_total['total'] += item[3]
        priority_total['blocker'] += item[4]
        priority_total['critical'] += item[5]
        priority_total['major'] += item[6]
        priority_total['minor'] += item[7]
        priority_total['trivial'] += item[8]

    context = RequestContext(request, {
        'form': form,
        'project': project,
        'weight_factor': sorted(weight_factor),
        'priority_total': priority_total,
        'component_names_standard': sorted(component_names_standard.keys()),
        'component_names': sorted([item for item in component_names_standard.keys() if item in component_names_without_slash]),
        'superuser': request.user.is_superuser,
    })
    return render(request, 'project_detail.html', context)


@login_required
def project_defects_density(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project_dds = ProjectComponentsDefectsDensity.objects.filter(project=project).order_by('version', 'created')

    version_names = []
    for project_dd in project_dds:
        version_names.append(project_dd.version)
    version_names = list(OrderedDict.fromkeys(version_names))

    #change '.' and ' ' to '_' from version names
    version_names_removed = []
    for version_name in version_names:
        version_names_removed.append(remove_period_space(version_name))

    jira_data = fetch_jira_data(project.jira_name)
    #check whether fetch the data from jira or not

    if jira_data == 'No JIRA Data':
        messages.warning(request, 'The project \"{0}\" does not exist in JIRA'.format(project.jira_name))
        context = RequestContext(request, {
        'project': project,
        'superuser': request.user.is_superuser,
        'no_jira_data': jira_data,
        })
        return render(request, 'projects_dd_start.html', context)
    else:
        weight_factor_versions = get_component_defects_density(request, jira_data)

    context = RequestContext(request, {
        'project': project,
        'project_dds': project_dds,
        'version_names': version_names_removed,
        'weight_factor_versions': weight_factor_versions,
        'component_names_standard': sorted(component_names_standard.keys()),
        'superuser': request.user.is_superuser
    })
    return render(request, 'projects_dd_start.html', context)


def get_component_defects_density_all(data, component_names_without_slash):

    #calculate issues number of components and sub-components
    """

    :param data: jira_data
    :param component_names_without_slash:
    :return: weight_factor
    """
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
    except FrameworkParameter.DoesNotExist or KeyError:
        jira_issue_weight_sum = Decimal(1.00)

    #calculate defect density of each component
    for item in component_names_without_slash:
        data[item]['total'] = data[item]['blocker'] * jira_issue_weight_sum * 5 / 15 \
                              + data[item]['critical'] * jira_issue_weight_sum * 4 / 15 \
                              + data[item]['major'] * jira_issue_weight_sum * 3 / 15 \
                              + data[item]['minor'] * jira_issue_weight_sum * 2 / 15 \
                              + data[item]['trivial'] * jira_issue_weight_sum * 1 / 15

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
        temp.append(data[item]['total'])   # defect density
        # Total number of issues
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

    return weight_factor


def get_component_defects_density(request, jira_data):
    version_names = []
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
        except FrameworkParameter.DoesNotExist or KeyError:
            jira_issue_weight_sum = Decimal(1.00)

        for item in version_data[key]:
            try:
                name = str(item['fields']['components'][0]['name'])
                component_names.append(name)
                component_names_without_slash.append(truncate_after_slash(name))
            except IndexError:
                continue
        component_names = list(OrderedDict.fromkeys(component_names))
        component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

        data = issue_counts_compute(request, component_names, component_names_without_slash, version_data[key])

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
            data[item]['total'] = data[item]['blocker'] * jira_issue_weight_sum * 5 / 15 \
                                  + data[item]['critical'] * jira_issue_weight_sum * 4 / 15 \
                                  + data[item]['major'] * jira_issue_weight_sum * 3 / 15 \
                                  + data[item]['minor'] * jira_issue_weight_sum * 2 / 15 \
                                  + data[item]['trivial'] * jira_issue_weight_sum * 1 / 15

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

        for item in sorted(component_names_without_slash):
            temp = []
            temp.append(item)
            try:
                temp.append(round(component_names_standard[item] / float(weight_factor_base), 3))
            except KeyError:
                continue
            temp.append(data[item]['total'])  #defect density
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
    return weight_factor_versions


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
            calculate_score(request, project)
    else:
        project = get_object_or_404(Project, pk=project_id)
        calculate_score(request, project)

    context = RequestContext(request, {
        'projects': projects,
        'framework_parameters': framework_parameters,
        'superuser': request.user.is_superuser
    })
    return render(request, 'projects_start.html', context)


def fetch_jira_data(jira_name):
    url = 'http://jira.west.com/rest/api/2/search?fields=components,status,priority,versions,issuetype&jql=project=' + jira_name
    data = requests.get(url, auth=('readonly_sliu_api_user', 'qualityengineering')).json()
    if len(data) == 2:
        if data['errorMessages']:
            return 'No JIRA Data'
    else:
        return data


def calculate_score(request, project):
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
    data = issue_counts_compute(request, component_names, component_names_without_slash, jira_data['issues'])

    #get framework parameter
    parameter = {}
    framework_parameters = FrameworkParameter.objects.all()
    for framework_parameter in framework_parameters:
        parameter[framework_parameter.parameter] = framework_parameter.value

    try:
        jira_issue_weight_sum = parameter['jira_issue_weight_sum']
    except KeyError:
        jira_issue_weight_sum = Decimal(1.00)
    #try:
    #    vaf_ratio = parameter['vaf_ratio']
    #except KeyError:
    #    vaf_ratio = Decimal(0.01)
    #try:
    #    vaf_exp = parameter['vaf_exp']
    #except KeyError:
    #    vaf_exp = Decimal(0.65)

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
        data[item]['total'] = data[item]['blocker'] * jira_issue_weight_sum * 5 / 15 \
                              + data[item]['critical'] * jira_issue_weight_sum * 4 / 15 \
                              + data[item]['major'] * jira_issue_weight_sum * 3 / 15 \
                              + data[item]['minor'] * jira_issue_weight_sum * 2 / 15 \
                              + data[item]['trivial'] * jira_issue_weight_sum * 1 / 15

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
    #test_character = project.accuracy + project.suitability + project.interoperability \
    #+ project.functional_security + project.usability + project.accessibility \
    #+ project.technical_security + project.reliability + project.efficiency \
    #+ project.maintainability + project.portability

    #vaf = vaf_ratio * test_character + vaf_exp   # VAF value
    score = (1 - raw_score) * 10  # projects score = 10 - defect score

    if score < 0:  # projects score out of range (0-10)
        project.score = -2
    elif score == 10:  # no open issues in JIRA
        project.score = -3
    else:
        project.score = round(score, 2)
    project.save()

    return round(score, 2)


def issue_counts_compute(request, component_names, component_names_without_slash, jira_data):
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

    #construct isstype filter
    # 1-Bug, 2-New Feature, 3-Task, 4-Improvement
    issue_types = ['1']
    if request: # daily_dd_log: request=None
        if request.user.usersettings.new_feature:
            issue_types.append('2')
        if request.user.usersettings.task:
            issue_types.append('3')
        if request.user.usersettings.improvement:
            issue_types.append('4')

    for item in jira_data:
        try:
            component = item['fields']['components'][0]['name']
            if item['fields']['status']['id'] in ['1', '3', '4', '5', '10001', '10003'] and \
                    item['fields']['issuetype']['id'] in issue_types:
            # 1-open, 3-In progress, 4-reopen, 5-resolved, 10001-UAT testing, 10003-Discovery
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


def fetch_defects_density_score(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project_dds = ProjectComponentsDefectsDensity.objects.filter(project=project)

    version_names = []
    for project_dd in project_dds:
        version_names.append(project_dd.version)
    version_names = list(OrderedDict.fromkeys(version_names))

    dd_trend_data = {}
    for version_name in version_names:
        data = {}
        #data['version'] = version_name

        tmp_categories = []

        tmp_data_voiceSlots = []
        tmp_data_cxp = []
        tmp_data_platform = []
        tmp_data_reports = []
        tmp_data_application = []

        tmp_data_ceeq = []
        tmp_data_ceeq_count = 0
        tmp_data_ceeq_sum = 0

        for item in project_dds:
            if item.version == version_name:
                #print item.created.month, item.created.day
                tmp_categories.append(str(item.created))

                tmp_data_voiceSlots.append(float(item.voiceSlots))
                tmp_data_cxp.append(float(item.cxp))
                tmp_data_platform.append(float(item.platform))
                tmp_data_reports.append(float(item.reports))
                tmp_data_application.append(float(item.application))

                tmp_data_ceeq.append(float(item.ceeq))
                tmp_data_ceeq_count += 1
                tmp_data_ceeq_sum += item.ceeq

        data['categories'] = tmp_categories
        data['voiceSlots'] = tmp_data_voiceSlots
        data['cxp'] = tmp_data_cxp
        data['platform'] = tmp_data_platform
        data['reports'] = tmp_data_reports
        data['application'] = tmp_data_application

        data['ceeq'] = tmp_data_ceeq
        data['ceeq_average'] = round(float(tmp_data_ceeq_sum / tmp_data_ceeq_count), 2)

        #change '.' and ' ' to '_' from version names
        dd_trend_data[remove_period_space(version_name)] = data

    return HttpResponse(json.dumps(dd_trend_data), content_type="application/json")


def fetch_defects_density_score_pie(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    jira_data = fetch_jira_data(project.jira_name)

    component_names = []
    component_names_without_slash = []

    for item in jira_data['issues']:
        try:
            name = str(item['fields']['components'][0]['name'])
            component_names.append(name)
            component_names_without_slash.append(truncate_after_slash(name))
        except IndexError:
            continue

    component_names = list(OrderedDict.fromkeys(component_names))
    component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

    data = issue_counts_compute(request, component_names, component_names_without_slash, jira_data['issues'])

    weight_factor = get_component_defects_density_all(data,
                                                      component_names_without_slash)

    # calculate total number of issues based on priority
    priority_total = {
        'total': 0,
        'blocker': 0,
        'critical': 0,
        'major': 0,
        'minor': 0,
        'trivial': 0
    }
    for item in weight_factor:
        priority_total['total'] += item[3]
        priority_total['blocker'] += item[4]
        priority_total['critical'] += item[5]
        priority_total['major'] += item[6]
        priority_total['minor'] += item[7]
        priority_total['trivial'] += item[8]

    dd_pie_data = []
    dd_pie_table = []
    dd_pie_graph = []

    for item in sorted(weight_factor):
        temp_graph = []
        temp_table = []

        temp_graph.append(item[0])
        temp_graph.append(float(item[1]) * float(item[2]))

        temp_table.append(item[0])
        temp_table.append(float(item[4]))
        temp_table.append(float(item[5]))
        temp_table.append(float(item[6]))
        temp_table.append(float(item[7]))
        temp_table.append(float(item[8]))
        temp_table.append(float(item[3]))

        dd_pie_graph.append(temp_graph)
        dd_pie_table.append(temp_table)

    temp_table = []
    temp_table.append('Total')
    temp_table.append(priority_total['blocker'])
    temp_table.append(priority_total['critical'])
    temp_table.append(priority_total['major'])
    temp_table.append(priority_total['minor'])
    temp_table.append(priority_total['trivial'])
    temp_table.append(priority_total['total'])

    dd_pie_table.append(temp_table)

    dd_pie_data.append(dd_pie_graph)
    dd_pie_data.append(dd_pie_table)

    return HttpResponse(json.dumps(dd_pie_data), content_type="application/json")


def defects_density_log(request, project_id):
    projects = Project.objects.all().order_by('name')
    framework_parameters = FrameworkParameter.objects.all()
    if project_id == '1000000':
        for project in projects:
            defects_density_single_log(request, project)
    else:
        project = Project.objects.get(pk=project_id)
        defects_density_single_log(request, project)

    context = RequestContext(request, {
        'projects': projects,
        'framework_parameters': framework_parameters,
        'superuser': request.user.is_superuser
    })

    return render(request, 'projects_start.html', context)


def defects_density_single_log(request, project):
    jira_data = fetch_jira_data(project.jira_name)

    #check whether fetch the data from jira or not

    if jira_data == 'No JIRA Data':
        messages.warning(request, 'The project \"{0}\" does not exist in JIRA'.format(project.jira_name))
        context = RequestContext(request, {
        'project': project,
        'superuser': request.user.is_superuser,
        'no_jira_data': jira_data,
        })
        return render(request, 'projects_dd_start.html', context)
    else:
        weight_factor_versions = get_component_defects_density(request, jira_data)

    today = date.today()
    for item in weight_factor_versions:
        ceeq_raw = 0  # calculate ceeq score per version
        for com in weight_factor_versions[item]:
            ceeq_raw += round(com[1] * float(com[2]), 3)
        #print ceeq_version
        try:
            component_defects_density = ProjectComponentsDefectsDensity.objects.get(project=project, version=item, created=today)
        except ProjectComponentsDefectsDensity.DoesNotExist:
            component_defects_density = ProjectComponentsDefectsDensity(project=project, version=item, created=today)

        # use ceeq field to store ceeq score
        component_defects_density.ceeq = (1 - ceeq_raw) * 10
        for component in weight_factor_versions[item]:
            #print item, component[0], component[2]
            if component[0] == 'CXP':
                component_defects_density.cxp = component[2]
            elif component[0] == 'Platform':
                component_defects_density.platform = component[2]
            elif component[0] == 'Reports':
                component_defects_density.reports = component[2]
            elif component[0] == 'Application':
                component_defects_density.application = component[2]
            elif component[0] == 'Voice Slots':
                component_defects_density.voiceSlots = component[2]
        component_defects_density.save()

    return


def remove_period_space(str):
    tmp = str.replace('.', '_')
    tmp = tmp.replace(' ', '_')
    tmp = tmp.replace(',', '_')
    return tmp