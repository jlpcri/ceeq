
import json
import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from collections import OrderedDict, defaultdict
from django.contrib.auth.decorators import login_required
from ceeq.apps.projects.utils import get_sub_component_weight_factor, get_component_names_from_jira_data
from ceeq.apps.projects.views import issue_counts_compute

from models import Project
from django.conf import settings

# Handling sub component pie chart

@login_required
def project_sub_piechart(request, project_id):
    uat_type = request.GET.get('uat_type')
    component_type = request.GET.get('component_type')

    if component_type == 'Application':
        sub_component_template = 'sub_component/project_sub_component_apps.html'
    elif component_type == 'CXP':
        sub_component_template = 'sub_component/project_sub_component_cxp.html'
    elif component_type == 'Platform':
        sub_component_template = 'sub_component/project_sub_component_platform.html'
    elif component_type == 'Reports':
        sub_component_template = 'sub_component/project_sub_component_reports.html'
    elif component_type == 'Voice Prompts':
        sub_component_template = 'sub_component/project_sub_component_voiceslots.html'
    else:
        sub_component_template = ''

    project = get_object_or_404(Project, pk=project_id)
    context = RequestContext(request, {
        'project': project,
        'uat_type': uat_type,
        'component_type': component_type,
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
        'uat_type_custom': request.GET.get('uat_type_custom', '')
    })
    return render(request, sub_component_template, context)


def fetch_subcomponents_pie_component(request, project_id):
    uat_type = request.GET.get('uat_type')
    component_type = request.GET.get('component_type')

    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    uat_type_custom = request.GET.get('uat_type_custom', '')

    component_name = [component_type]

    sub_pie_data = fetch_subcomponents_pie(request, project_id, component_name, uat_type, start, end, uat_type_custom)

    return HttpResponse(json.dumps(sub_pie_data), content_type='application/json')


def fetch_subcomponents_pie(request, project_id, component_name, uat_type, start, end, uat_type_custom):
    """
    Used for pie chart along with drawing data table of Subcomponents of Applications
    :param request:
    :param project_id:
    :return:
    """

    project = get_object_or_404(Project, pk=project_id)

    jira_data = project.fetch_jira_data

    version_data = jira_data['issues']

    #print uat_type, start, end, uat_type_custom
    version_data_custom = []
    if uat_type == 'custom':
        start_date = datetime.datetime.fromtimestamp(int(start)).strftime('%Y-%m-%d')
        end_date = datetime.datetime.fromtimestamp(int(end)).strftime('%Y-%m-%d')

        for item in version_data:
            if start_date <= item['fields']['created'] <= end_date:
                version_data_custom.append(item)
        version_data = version_data_custom

    #component_name = ['Application']
    sub_component_names = []

    for item in version_data:
        # if first item-component is not in framework, then check next, until end
        component_len = len(item['fields']['components'])
        if component_len == 0:
            continue
        else:
            name = get_component_names_from_jira_data(component_len, item['fields']['components'])

        if name and name.startswith(component_name[0]):
            sub_component_names.append(name)

    sub_component_names = list(OrderedDict.fromkeys(sub_component_names))
    if component_name[0] in sub_component_names:
        return 'component configuration issue'

    if uat_type == 'custom':
        data = issue_counts_compute(request,
                                    sub_component_names,
                                    component_name, version_data,
                                    'sub_components',
                                    uat_type_custom)
    else:
        data = issue_counts_compute(request,
                                    sub_component_names,
                                    component_name, version_data,
                                    'sub_components',
                                    uat_type)

    weight_factor = get_sub_component_weight_factor(data, component_name[0], 1)
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
        for status in settings.ISSUE_STATUS_FIELDS:
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
    for status in settings.ISSUE_STATUS_FIELDS:
        temp_table.append(priority_total[status[0]])
        temp_table.append(None)
        temp_table.append(None)
    temp_table.append(priority_total['total'])

    sub_pie_data.append(sub_pie_graph)
    sub_pie_data.append(sub_pie_table)
    sub_pie_data.append(temp_table)

    #print sub_pie_data

    return sub_pie_data


