from datetime import date
from decimal import Decimal
import json
import copy

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from collections import OrderedDict, defaultdict
from django.contrib.auth.decorators import login_required, user_passes_test
from ceeq.apps.projects.utils import remove_period_space, truncate_after_slash, version_name_from_jira_data, \
    project_detail_calculate_score, get_weight_factor, get_subcomponent_defects_density, issue_counts_compute
from ceeq.apps.users.views import user_is_superuser

from models import Project, FrameworkParameter, ProjectComponentsDefectsDensity
from forms import ProjectForm, ProjectNewForm
from ceeq.settings.base import component_names_standard,\
    issue_status_count, issue_status_open, issue_status_resolved, issue_status_closed, \
    issue_status_fields, issue_resolution_not_count


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


@login_required
def project_detail(request, project_id):
    """
    Detail page of project, include pie chart, data table of component
    :param request:
    :param project_id:
    :return:
    """
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(instance=project)

    component_names = []
    component_names_without_slash = []

    try:
        jira_data = project.fetch_jira_data
    except ValueError:
        messages.warning(request, 'Cannot Access to JIRA')
        return render(request, 'home.html')

    #check whether fetch the data from jira or not
    if jira_data == 'No JIRA Data':
        messages.warning(request, 'The project \"{0}\" does not exist in JIRA'.format(project.jira_name))
        context = RequestContext(request, {
            'form': form,
            'project': project,
            'superuser': request.user.is_superuser,
            'no_jira_data': jira_data,
            'version_names': ['All Versions']
        })
        return render(request, 'project_detail.html', context)

    #List for choice of jira verion per project
    version_names = project.fectch_jira_versions
    #version_names = version_name_from_jira_data(jira_data)
    #version_names.append('All Versions')

    # get jira_data based on version
    if project.jira_version == 'All Versions':
        version_data = jira_data['issues']
    else:
        version_data = []
        for item in jira_data['issues']:
            try:
                name = str(item['fields']['versions'][0]['name'])
            except UnicodeEncodeError:
                name = u''.join(item['fields']['versions'][0]['name']).encode('utf-8').strip()
            except IndexError:
                continue
            if name.decode('utf-8') == project.jira_version:
                version_data.append(item)

    # Try get pie chart data
    dd_pie_data = fetch_defects_density_score_pie(request, project.jira_name, version_data)
    #print dd_pie_data

    for item in version_data:
        try:
            name = str(item['fields']['components'][0]['name'])
        except UnicodeEncodeError:
            name = ''.join(item['fields']['components'][0]['name']).encode('utf-8').strip()
        except IndexError:
            continue
        component_names.append(name)
        component_names_without_slash.append(truncate_after_slash(name))

    component_names = list(OrderedDict.fromkeys(component_names))
    component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

    #print component_names_without_slash
    data = issue_counts_compute(request, component_names, component_names_without_slash, version_data, 'components')
    #print data
    weight_factor = get_weight_factor(data, component_names_without_slash)

    #update ceeq score
    project.score = project_detail_calculate_score(weight_factor)
    project.save()

    # calculate total number of issues based on priority
    priority_total = defaultdict(int)

    for item in weight_factor:
        #print item
        priority_total['total'] += item[3]
        for status in issue_status_fields:
            priority_total[status[0]] += sum(item[i] for i in status[1])

    try:
        component_names_exist = list(zip(*weight_factor)[0])
    except IndexError:
        component_names_exist = None

    context = RequestContext(request, {
        'form': form,
        'project': project,
        'weight_factor': weight_factor,
        'priority_total': priority_total,
        'component_names_standard': sorted(component_names_standard.keys()),
        'component_names': component_names_exist,
        'superuser': request.user.is_superuser,
        'version_names': version_names,
        'dd_pie_data': json.dumps(dd_pie_data)
    })
    return render(request, 'project_detail.html', context)


@login_required
def project_defects_density(request, project_id):
    """
    Include trending graph of defects density and ceeq score per version
    :param request:
    :param project_id:
    :return: component weight, dds, priority-status, trending graph
    """
    project = get_object_or_404(Project, pk=project_id)
    project_dds = ProjectComponentsDefectsDensity.objects.filter(project=project, version=project.jira_version).order_by('version', 'created')

    version_names = []
    for project_dd in project_dds:
        version_names.append(project_dd.version)
    version_names = list(OrderedDict.fromkeys(version_names))

    #change '.' and ' ' to '_' from version names
    version_names_removed = []
    for version_name in version_names:
        version_names_removed.append(remove_period_space(version_name))

    try:
        jira_data = project.fetch_jira_data
    except ValueError:
        messages.warning(request, 'Cannot Access to JIRA')
        return render(request, 'home.html')

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


def get_component_defects_density(request, jira_data):
    """
    Get component defects density based on versions
    :param request:
    :param jira_data:
    :return:
    """

    version_names = version_name_from_jira_data(jira_data)

    version_data = {}
    for version_name in version_names:
        temp_data = []
        for item in jira_data['issues']:
            try:
                name = str(item['fields']['versions'][0]['name'])
            except UnicodeEncodeError:
                name = u''.join(item['fields']['versions'][0]['name']).encode('utf-8').strip()
            except IndexError:
                continue
            if name.decode('utf-8') == version_name:
                temp_data.append(item)

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
            except UnicodeEncodeError:
                name = ''.join(item['fields']['components'][0]['name']).encode('utf-8').strip()
            except IndexError:
                continue
            component_names.append(name)
            component_names_without_slash.append(truncate_after_slash(name))

        component_names = list(OrderedDict.fromkeys(component_names))
        component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

        data = issue_counts_compute(request, component_names, component_names_without_slash, version_data[key], 'components')

        #calculate issues number of components and sub-components
        weight_factor_versions[key] = get_weight_factor(data, component_names_without_slash)

    return weight_factor_versions



@user_passes_test(user_is_superuser)
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            #messages.success(request, "Projects info has been saved.")
            return redirect(project_detail, project.id)
        else:
            messages.error(request, "Correct errors in the form.")
            context = RequestContext(request, {
                'form': form,
                'project': project,
                'superuser': request.user.is_superuser,
                'version_names': ['All Versions']
            })
            return render(request, 'project_detail.html', context)
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
            return render(request, 'project_new.html', context)
    else:
        form = ProjectNewForm()
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
    """
    Calculate ceeq score all projects
    :param request:
    :param project_id:
    :return:
    """
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


def calculate_score(request, project):
    """
    Calculate ceeq score per project
    :param request:
    :param project: which ceeq score need to be calculated
    :return: ceeq score is saved to project and returned
    """
    # Get component names for autocomplete
    component_names = []
    component_names_without_slash = []

    try:
        jira_data = project.fetch_jira_data
    except ValueError:
        messages.warning(request, 'Cannot Access to JIRA')
        return render(request, 'home.html')

    # check whether fetch the data from JIRA or not
    if jira_data == 'No JIRA Data':
        project.score = 104
        project.save()
        return

    #get jira data based on version
    if project.jira_version == 'All Versions':
        version_data = jira_data['issues']
    else:
        version_data = []
        for item in jira_data['issues']:
            try:
                name = str(item['fields']['versions'][0]['name'])
            except UnicodeEncodeError:
                name = u''.join(item['fields']['versions'][0]['name']).encode('utf-8').strip()
            except IndexError:
                continue
            if name.decode('utf-8') == project.jira_version:
                version_data.append(item)

    for item in version_data:
        try:
            name = str(item['fields']['components'][0]['name'])
        except UnicodeEncodeError:
            name = ''.join(item['fields']['components'][0]['name']).encode('utf-8').strip()
        except IndexError:
            continue
        component_names.append(name)
        component_names_without_slash.append(truncate_after_slash(name))

    component_names = list(OrderedDict.fromkeys(component_names))
    component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

    # Construct # of different priority issues dict from jira_data
    data = issue_counts_compute(request, component_names, component_names_without_slash, version_data, 'components')

    weight_factor = get_weight_factor(data, component_names_without_slash)

    # Calculate Raw Score of project
    raw_score = 0
    for item in weight_factor:
        raw_score += Decimal(item[1]) * item[2]   # item[1]: component weight, float, item[2]: defects density, decimal

    #print round(raw_score, 2)

    #Calculate VAF(Value Adjustment Factor)
    #test_character = project.accuracy + project.suitability + project.interoperability \
    #+ project.functional_security + project.usability + project.accessibility \
    #+ project.technical_security + project.reliability + project.efficiency \
    #+ project.maintainability + project.portability

    #vaf = vaf_ratio * test_character + vaf_exp   # VAF value
    score = (1 - raw_score) * 10  # projects score = 10 - defect score

    if score < 0:  # projects score out of range (0-10)
        #project.score = 20
        project.score = round(score, 2)
    elif score == 10:  # no open issues in JIRA
        project.score = 103
    else:
        project.score = round(score, 2)
    project.save()

    return round(score, 2)


def fetch_projects_score(request):
    """
    Use for ceeq score bar graph
    :param request:
    :return: json data
            categories: Y axis label
            score: X axis value
            id: project id for hyperlink of project detail
    """
    projects = Project.objects.all().order_by('name')
    data = {}

    data['categories'] = [project.name for project in projects]
    # score = 102 represents it is below zero
    data['score'] = [str(project.score) if project.score < 10 else str(0) for project in projects]
    data['id'] = [str(project.id) for project in projects]

    return HttpResponse(json.dumps(data), content_type="application/json")


def fetch_defects_density_score(request, project_id):
    """
    Used for trending defects density graph and trending ceeq score graph
    :param request:
    :param project_id:
    :return: json data include average ceeq score per version
    """
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
                if item.created.month < 10:
                    tmp_month = '0' + str(item.created.month)
                else:
                    tmp_month = str(item.created.month)
                if item.created.day < 10:
                    tmp_day = '0' + str(item.created.day)
                else:
                    tmp_day = str(item.created.day)
                #print tmp_month + '-' + tmp_day
                tmp_categories.append(tmp_month + '-' + tmp_day)

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


def fetch_defects_density_score_pie(request, jira_name, version_data):
    """
    Used for pie chart along with drawing data table
    :param request:
    :param jira_name:
    :version_data:
    :return:
    """
    component_names = []
    component_names_without_slash = []

    for item in version_data:
        try:
            name = str(item['fields']['components'][0]['name'])
        except UnicodeEncodeError:
            name = ''.join(item['fields']['components'][0]['name']).encode('utf-8').strip()
        except IndexError:
            continue
        component_names.append(name)
        component_names_without_slash.append(truncate_after_slash(name))

    component_names = list(OrderedDict.fromkeys(component_names))
    component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

    data = issue_counts_compute(request, component_names, component_names_without_slash, version_data, 'components')

    weight_factor = get_weight_factor(data, component_names_without_slash)
    #print weight_factor

    # calculate total number of issues based on priority
    priority_total = defaultdict(int)

    dd_pie_data = []
    dd_pie_table = []
    dd_pie_graph = []
    donut_pie_inner = []
    donut_pie_outer = []

    for item in weight_factor:
        temp_graph = []  # data for Component as outer ring
        #temp_graph_subcomponent = []  # data for subcomponent as inner ring
        temp_table = []

        temp_graph.append(item[0])
        temp_graph.append(float(item[1]) * float(item[2]))
        # for color index
        temp_graph.append(sorted(component_names_standard.keys()).index(item[0]))

        temp_graph_subcomponent = get_subcomponent_defects_density(request, item[0], version_data)

        priority_total['total'] += item[3]  # Total of all issues of pie chart table
        temp_table.append(item[0])  # Component name

        # number of issues Open, Resolved, Closed
        for status in issue_status_fields:
            for i in status[1]:
                priority_total[status[0]] += item[i]
                temp_table.append(float(item[i]))

        temp_table.append(None)
        temp_table.append(float(item[3]))   # SubTotal of pie chart table

        dd_pie_table.append(temp_table)
        donut_pie_inner.append(temp_graph)
        donut_pie_outer.append(temp_graph_subcomponent)

    for item in sorted(component_names_standard.keys()):
        temp_table = []
        try:
            if item not in list(zip(*weight_factor)[0]):
                temp_table.append(item)
                for status in issue_status_fields:
                    for i in status[1]:
                        temp_table.append(0)
                temp_table.append(None)
                temp_table.append(0)

                dd_pie_table.append(temp_table)
        except IndexError:
            continue

    temp_table = []
    temp_table.append('Total')
    temp_table.append(None)
    for status in issue_status_fields:  # total number per priority
        temp_table.append(priority_total[status[0]])
        temp_table.append(None)
        temp_table.append(None)
    temp_table.append(priority_total['total'])

    #print 'old: ', dd_pie_graph

    dd_pie_graph.append(donut_pie_inner)
    dd_pie_graph.append(donut_pie_outer)
    #print 'new: ', dd_pie_graph_new

    dd_pie_data.append(dd_pie_graph)
    dd_pie_data.append(dd_pie_table)
    dd_pie_data.append(temp_table)
    #dd_pie_data.append((jira_name, request.user.is_superuser))

    return dd_pie_data


def defects_density_log(request, project_id):
    """
    Record defects density per version for all projects
    :param request:
    :param project_id:
    :return:
    """
    projects = Project.objects.all().order_by('name')
    framework_parameters = FrameworkParameter.objects.all()
    if project_id == '1000000':
        for project in projects:
            defects_density_single_log(request, project)
    else:
        #project = Project.objects.get(pk=project_id)
        project = get_object_or_404(Project, pk=project_id)
        defects_density_single_log(request, project)

    context = RequestContext(request, {
        'projects': projects,
        'framework_parameters': framework_parameters,
        'superuser': request.user.is_superuser
    })

    return render(request, 'projects_start.html', context)


def defects_density_single_log(request, project):
    """
    Record defects density per version for per project
    :param request:
    :param project:
    :return:
    """
    try:
        jira_data = project.fetch_jira_data
    except ValueError:
        messages.warning(request, 'Cannot Access to JIRA')
        return render(request, 'home.html')

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


