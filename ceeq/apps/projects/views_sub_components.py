
import json

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from collections import OrderedDict, defaultdict
from django.contrib.auth.decorators import user_passes_test
from ceeq.apps.projects.views import issue_counts_compute
from ceeq.apps.users.views import user_is_superuser

from models import Project
from ceeq.settings.base import issue_priority_weight,\
    issue_status_count, issue_status_weight, \
    issue_status_fields

# Handling sub component pie chart
@user_passes_test(user_is_superuser)
def project_sub_apps_piechart(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context = RequestContext(request, {
        'project': project
    })
    return render(request, 'project_sub_component_apps.html', context)


def project_sub_cxp_piechart(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context = RequestContext(request, {
        'project': project
    })
    return render(request, 'project_sub_component_cxp.html', context)


def project_sub_platform_piechart(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context = RequestContext(request, {
        'project': project
    })
    return render(request, 'project_sub_component_platform.html', context)


def project_sub_reports_piechart(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context = RequestContext(request, {
        'project': project
    })
    return render(request, 'project_sub_component_reports.html', context)


def fetch_apps_subcomponents_pie(request, project_id):
    component_name = ['Application']
    sub_pie_data = fetch_subcomponents_pie(request, project_id, component_name)

    return HttpResponse(json.dumps(sub_pie_data), content_type='application/json')


def fetch_reports_subcomponents_pie(request, project_id):
    component_name = ['Reports']
    sub_pie_data = fetch_subcomponents_pie(request, project_id, component_name)

    return HttpResponse(json.dumps(sub_pie_data), content_type='application/json')


def fetch_cxp_subcomponents_pie(request, project_id):
    component_name = ['CXP']
    sub_pie_data = fetch_subcomponents_pie(request, project_id, component_name)

    return HttpResponse(json.dumps(sub_pie_data), content_type='application/json')


def fetch_platform_subcomponents_pie(request, project_id):
    component_name = ['Platform']
    sub_pie_data = fetch_subcomponents_pie(request, project_id, component_name)

    return HttpResponse(json.dumps(sub_pie_data), content_type='application/json')


def fetch_subcomponents_pie(request, project_id, component_name):
    """
    Used for pie chart along with drawing data table of Subcomponents of Applications
    :param request:
    :param project_id:
    :return:
    """

    project = get_object_or_404(Project, pk=project_id)

    jira_data = project.fetch_jira_data
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

    #component_name = ['Application']
    sub_component_names = []

    for item in version_data:
        try:
            name = str(item['fields']['components'][0]['name'])
            if name.startswith(component_name[0]):
                sub_component_names.append(name)
        except IndexError:
            continue

    sub_component_names = list(OrderedDict.fromkeys(sub_component_names))
    if component_name[0] in sub_component_names:
        return 'component configuration issue'


    data = issue_counts_compute(request, sub_component_names, component_name, version_data, 'sub_components')

    weight_factor = get_sub_component_weight_factor(data)
    #for item in weight_factor:
    #    print item, weight_factor[item]

    priority_total = defaultdict(int)

    sub_pie_data = []
    sub_pie_table = []
    sub_pie_graph = []

    for item in data:
        if item == component_name[0] or sum(data[item]['total'].itervalues()) == 0:
            continue
        temp_graph = []
        temp_table = []
        sub_total = 0

        priority_total['total'] += sum(data[item]['total'].itervalues())

        temp_graph.append(item[len(component_name[0]) + 1:])
        temp_graph.append(float(sum(data[item]['ceeq'].itervalues())))

        temp_table.append(item[len(component_name[0]) + 1:])
        for status in issue_status_fields:
            temp_table.append(float(data[item][status[0]]['open']))
            temp_table.append(float(data[item][status[0]]['resolved']))
            temp_table.append(float(data[item][status[0]]['closed']))

            sub_total += sum(data[item][status[0]].itervalues())

            priority_total[status[0]] += sum(data[item][status[0]].itervalues())

        temp_table.append(None)
        temp_table.append(sub_total)

        sub_pie_graph.append(temp_graph)
        sub_pie_table.append(temp_table)

    temp_table = []
    temp_table.append('Total')
    temp_table.append(None)
    for status in issue_status_fields:
        temp_table.append(priority_total[status[0]])
        temp_table.append(None)
        temp_table.append(None)
    temp_table.append(priority_total['total'])

    sub_pie_data.append(sub_pie_graph)
    sub_pie_data.append(sub_pie_table)
    sub_pie_data.append(temp_table)

    #print sub_pie_data

    return sub_pie_data


def get_sub_component_weight_factor(data):
    for item in data:
        for status in issue_status_count.keys():
            # total number of jiras per sub component
            data[item]['total'][status] = data[item]['blocker'][status] \
                                        + data[item]['critical'][status] \
                                        + data[item]['major'][status] \
                                        + data[item]['minor'][status] \
                                        + data[item]['trivial'][status]

            # defects density per sub component
            data[item]['ceeq'][status] = data[item]['blocker'][status] * issue_status_weight[status] * issue_priority_weight['blocker'] \
                                + data[item]['critical'][status] * issue_status_weight[status] * issue_priority_weight['critical'] \
                                + data[item]['major'][status] * issue_status_weight[status] * issue_priority_weight['major'] \
                                + data[item]['minor'][status] * issue_status_weight[status] * issue_priority_weight['minor'] \
                                + data[item]['trivial'][status] * issue_status_weight[status] * issue_priority_weight['trivial']

    return data