from collections import OrderedDict, defaultdict
import copy
from decimal import Decimal
from operator import itemgetter
from datetime import datetime
from django.db.models import Max
from django.shortcuts import get_object_or_404

from ceeq.apps.calculator.models import SeverityMap, LiveSettings, ComponentImpact, ResultHistory

# define globe variables
from ceeq.apps.queries.models import Project
from ceeq.apps.queries.models import ScoreHistory

ISSUE_STATUS_OPEN = ['Open', 'In Progress', 'Reopened', 'Discovery', 'Review', 'Pending', 'Research']
ISSUE_STATUS_RESOLVED = ['Resolved', 'UAT Testing']
ISSUE_STATUS_CLOSED = ['Closed']
# issue status weight ratio
ISSUE_STATUS_WEIGHT = {
    'open': Decimal(7) / 10,
    'resolved': Decimal(2) / 10,
    'closed': Decimal(1) / 10,
}

ISSUE_PRIORITY_BLOCKER = 'Blocker'
ISSUE_PRIORITY_CRITICAL = 'Critical'
ISSUE_PRIORITY_MAJOR = 'Major'
ISSUE_PRIORITY_MINOR = 'Minor'
ISSUE_PRIORITY_TRIVIAL = 'Trivial'

# index of Open Resolved Closed issues per priority
ISSUE_STATUS_FIELDS = [
        ('blocker', [5, 6, 4]),
        ('critical', [8, 9, 7]),
        ('major', [11, 12, 10]),
        ('minor', [14, 15, 13]),
        ('trivial', [17, 18, 16])
    ]

# Priority Weight of Issues in JIRA
try:
    severity_map = SeverityMap.objects.get(name='current')
    severity_total = severity_map.blocker \
                     + severity_map.critical \
                     + severity_map.major \
                     + severity_map.minor \
                     + severity_map.trivial
    ISSUE_PRIORITY_WEIGHT = {
        'blocker': Decimal(severity_map.blocker) / severity_total,
        'critical': Decimal(severity_map.critical) / severity_total,
        'major': Decimal(severity_map.major) / severity_total,
        'minor': Decimal(severity_map.minor) / severity_total,
        'trivial': Decimal(severity_map.trivial) / severity_total,

    }
except SeverityMap.DoesNotExist:
    ISSUE_PRIORITY_WEIGHT = {
        'blocker': Decimal(5) / 15,
        'critical': Decimal(4) / 15,
        'major': Decimal(3) / 15,
        'minor': Decimal(2) / 15,
        'trivial': Decimal(1) / 15
    }

ISSUE_STATUS_COUNT = {
    'open': 0,
    'resolved': 0,
    'closed': 0,
}


def get_score_data(project, query_results, uat_type):
    data = {}
    component_names = []
    component_names_without_slash = []

    for item in query_results:
        component_names.append(item['components'])
        component_names_without_slash.append(truncate_after_slash(item['components']))

    component_names = list(OrderedDict.fromkeys(component_names))
    component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

    # print component_names
    # print component_names_without_slash

    # calculate issue counts
    data_issue_counts = issue_counts_compute(component_names,
                                             component_names_without_slash,
                                             query_results,
                                             'components',  # calculation for Components or Sub Components
                                             uat_type)

    # Framework of Apps/Inbound/Outbound etc component:weight
    frame_components = get_framework_components_weight(project)

    weight_factor = get_weight_factor(data_issue_counts,
                                      component_names_without_slash,
                                      frame_components)

    # calculate CEEQ score
    score = calculate_ceeq_score(weight_factor)

    # get exist component name
    try:
        component_names_exist = list(zip(*weight_factor)[0])
    except IndexError:
        component_names_exist = None

    # get priority total number of JIRA from weight_factor
    priority_total = defaultdict(int)
    for item in weight_factor:
        priority_total['total'] += item[3]
        for status in ISSUE_STATUS_FIELDS:
            priority_total[status[0]] += sum(item[i] for i in status[1])

    # get pie chart data
    pie_chart_data = get_pie_chart_data(data_issue_counts,
                                        weight_factor,
                                        query_results,
                                        uat_type,
                                        frame_components,
                                        score[0])

    # get ceeq trend graph
    ceeq_trend_graph = get_ceeq_trend_graph(project, uat_type)

    data['score'] = score
    data['weight_factor'] = weight_factor
    data['components_exist'] = component_names_exist
    data['priority_total'] = priority_total
    data['pie_chart_data'] = pie_chart_data
    data['ceeq_trend_graph'] = ceeq_trend_graph

    return data


def get_score_by_component(query_results, uat_type):
    """
    Calculate CEEQ score by each component without other components
    :param query_results:
    :param uat_type:
    :return:
    """
    pass


def truncate_after_slash(string):
    if string and '/' in string:
        index = string.index('/')
        return string[:index]
    else:
        return string


def issue_counts_compute(component_names, component_names_without_slash, jira_data, component_type, uat_type):
    """
    Compute number of issues Component, SubComponent, Priority, Status
    :param request:
    :param component_names: include SubComponents
    :param component_names_without_slash: without SubComponents
    :param jira_data: raw data from Query Results
    :param component_type: calculate based on Components or SubComponents
    :return: dictionary data
    """
    data = {}
    issue_counts = {
        'ceeq': ISSUE_STATUS_COUNT.copy(),  # store ceeq score
        'total': ISSUE_STATUS_COUNT.copy(),  # total number of jira per component/sub component
        'blocker': ISSUE_STATUS_COUNT.copy(),
        'critical': ISSUE_STATUS_COUNT.copy(),
        'major': ISSUE_STATUS_COUNT.copy(),
        'minor': ISSUE_STATUS_COUNT.copy(),
        'trivial': ISSUE_STATUS_COUNT.copy(),
        'ceeq_closed': ISSUE_STATUS_COUNT.copy()  # for if all JIRAs are closed
    }

    for item in component_names:
        data[item] = copy.deepcopy(issue_counts)  # copy the dict object

    for item in component_names_without_slash:  # add component item to data
        if item in data.keys():
            continue
        else:
            data[item] = copy.deepcopy(issue_counts)

    for item in jira_data:
        if uat_type == 'include_uat':
            pass
        elif uat_type == 'exclude_uat':
            # UAT workflow metatype not counted
            try:
                if item['customfield_13286']:
                    continue
            except KeyError:
                pass
        elif uat_type == 'only_uat':
            # Only workflow metatype counted
            try:
                if not item['customfield_13286']:
                    continue
            except KeyError:
                pass

        component = item['components']
        if component_type == 'sub_components' and not component.startswith(component_names_without_slash[0]):
            continue

        if item['status'] in ISSUE_STATUS_OPEN:
            if item['priority'] == ISSUE_PRIORITY_BLOCKER:
                data[component]['blocker']['open'] += 1
            elif item['priority'] == ISSUE_PRIORITY_CRITICAL:
                data[component]['critical']['open'] += 1
            elif item['priority'] == ISSUE_PRIORITY_MAJOR:
                data[component]['major']['open'] += 1
            elif item['priority'] == ISSUE_PRIORITY_MINOR:
                data[component]['minor']['open'] += 1
            elif item['priority'] == ISSUE_PRIORITY_TRIVIAL:
                data[component]['trivial']['open'] += 1
        elif item['status'] in ISSUE_STATUS_RESOLVED:
            if item['priority'] == ISSUE_PRIORITY_BLOCKER:
                data[component]['blocker']['resolved'] += 1
            elif item['priority'] == ISSUE_PRIORITY_CRITICAL:
                data[component]['critical']['resolved'] += 1
            elif item['priority'] == ISSUE_PRIORITY_MAJOR:
                data[component]['major']['resolved'] += 1
            elif item['priority'] == ISSUE_PRIORITY_MINOR:
                data[component]['minor']['resolved'] += 1
            elif item['priority'] == ISSUE_PRIORITY_TRIVIAL:
                data[component]['trivial']['resolved'] += 1
        elif item['status'] in ISSUE_STATUS_CLOSED:
            if item['priority'] == ISSUE_PRIORITY_BLOCKER:
                data[component]['blocker']['closed'] += 1
            elif item['priority'] == ISSUE_PRIORITY_CRITICAL:
                data[component]['critical']['closed'] += 1
            elif item['priority'] == ISSUE_PRIORITY_MAJOR:
                data[component]['major']['closed'] += 1
            elif item['priority'] == ISSUE_PRIORITY_MINOR:
                data[component]['minor']['closed'] += 1
            elif item['priority'] == ISSUE_PRIORITY_TRIVIAL:
                data[component]['trivial']['closed'] += 1

    return data


def get_weight_factor(data, component_names_without_slash, frame_components):
    for component in component_names_without_slash:
        for item in data:
            if item.startswith(component + '/'):
                for status in ISSUE_STATUS_COUNT.keys():
                    # total number of jiras per sub component
                    data[item]['total'][status] = data[item]['blocker'][status]\
                                                  + data[item]['critical'][status]\
                                                  + data[item]['major'][status]\
                                                  + data[item]['minor'][status] \
                                                  + data[item]['trivial'][status]

                    # defects density per sub component
                    data[item]['ceeq'][status] = data[item]['blocker'][status] * ISSUE_STATUS_WEIGHT[status] * ISSUE_PRIORITY_WEIGHT['blocker']\
                                                 + data[item]['critical'][status] * ISSUE_STATUS_WEIGHT[status] * ISSUE_PRIORITY_WEIGHT['critical']\
                                                 + data[item]['major'][status] * ISSUE_STATUS_WEIGHT[status] * ISSUE_PRIORITY_WEIGHT['major'] \
                                                 + data[item]['minor'][status] * ISSUE_STATUS_WEIGHT[status] * ISSUE_PRIORITY_WEIGHT['minor'] \
                                                 + data[item]['trivial'][status] * ISSUE_STATUS_WEIGHT[status] * ISSUE_PRIORITY_WEIGHT['trivial']

                    # defects density per sub component if all closed
                    data[item]['ceeq_closed'][status] = data[item]['blocker'][status] * ISSUE_STATUS_WEIGHT['closed'] * ISSUE_PRIORITY_WEIGHT['blocker']\
                                                        + data[item]['critical'][status] * ISSUE_STATUS_WEIGHT['closed'] * ISSUE_PRIORITY_WEIGHT['critical']\
                                                        + data[item]['major'][status] * ISSUE_STATUS_WEIGHT['closed'] * ISSUE_PRIORITY_WEIGHT['major'] \
                                                        + data[item]['minor'][status] * ISSUE_STATUS_WEIGHT['closed'] * ISSUE_PRIORITY_WEIGHT['minor'] \
                                                        + data[item]['trivial'][status] * ISSUE_STATUS_WEIGHT['closed'] * ISSUE_PRIORITY_WEIGHT['trivial']

                    data[component]['blocker'][status] += data[item]['blocker'][status]
                    data[component]['critical'][status] += data[item]['critical'][status]
                    data[component]['major'][status] += data[item]['major'][status]
                    data[component]['minor'][status] += data[item]['minor'][status]
                    data[component]['trivial'][status] += data[item]['trivial'][status]

                    data[component]['total'][status] += data[item]['total'][status]

    # for i in data:
    #     print i, data[i]

    # calculate defect density of each component
    for component in component_names_without_slash:
        for item in data:
            if item.startswith(component + '/'):
                for status in ISSUE_STATUS_COUNT.keys():
                    data[component]['ceeq'][status] += data[item]['ceeq'][status]
                    data[component]['ceeq_closed'][status] += data[item]['ceeq_closed'][status]

    # formalize total sum of each component: divided by number of sub-components
    for component in component_names_without_slash:
        subcomponent_length = 0
        for item in data:
            if item.startswith(component + '/') and sum(data[item]['ceeq'].itervalues()) > 0:
                subcomponent_length += 1
            else:
                continue

        if subcomponent_length == 0:
            continue
        else:
            for status in ISSUE_STATUS_WEIGHT.keys():
                data[component]['ceeq'][status] /= subcomponent_length
                data[component]['ceeq_closed'][status] /= subcomponent_length

    weight_factor = []
    try:
        ls = LiveSettings.objects.get(pk=1)
        score_scalar = ls.score_scalar
    except LiveSettings.DoesNotExist:
        score_scalar = 20

    for item in sorted(component_names_without_slash):
        temp = []
        # Skip the component with zero issues
        if sum(data[item]['total'].itervalues()) == 0:
            continue
        temp.append(item)
        try:
            # dynamically component weight, float
            temp.append(round(frame_components[item] / score_scalar, 3))
        except KeyError:
            continue

        temp.append(round(sum(data[item]['ceeq'].itervalues()), 3))  # defect density, decimal
        temp.append(sum(data[item]['total'].itervalues()))  # total number per component

        for priority in sorted(ISSUE_PRIORITY_WEIGHT.keys()):
            for status in sorted(ISSUE_STATUS_COUNT.keys()):
                try:
                    temp.append(data[item][priority][status])
                except KeyError:
                    continue

        temp.append(round(sum(data[item]['ceeq_closed'].itervalues()), 3))  # defect density if all closed, decimal

        weight_factor.append(temp)

    return weight_factor


def get_framework_components_weight(project):
    frame_components = {}
    components = ComponentImpact.objects.filter(impact_map=project.impact_map)
    for item in components:
        frame_components[item.component_name] = item.impact

    return frame_components


def calculate_ceeq_score(weight_factor):
    ceeq_raw = 0
    ceeq_closed_raw = 0
    for item in weight_factor:
        ceeq_raw += Decimal(item[1] * item[2])  # item[1]: component weight, float, item[2]: defects density, decimal
        ceeq_closed_raw += Decimal(item[1] * item[19])  # item[1]: component weight, item[19]: defects density if all closed
    ceeq_raw = (1 - ceeq_raw) * 10
    ceeq_closed_raw = (1 - ceeq_closed_raw) * 10

    if ceeq_raw == 10:  # no open issues in JIRA
        score = 103
        score_closed = 103
    else:
        score = round(ceeq_raw, 2)
        score_closed = round(ceeq_closed_raw, 2)

    data = []
    data.append(score)
    data.append(score_closed)
    return data


def get_pie_chart_data(data_issue_counts, weight_factor, query_results, uat_type, frame_components, uat_score):
    # calculate total number of issues based on priority
    priority_total = defaultdict(int)

    dd_pie_data = []
    dd_pie_table = []
    dd_pie_graph = []
    donut_pie_inner = []
    donut_pie_outer = []

    for item in weight_factor:
        temp_graph = []  # data for Component as outer ring
        temp_table = []

        temp_graph.append(item[0])
        temp_graph.append(item[1] * item[2])
        # for color index
        temp_graph.append(sorted(frame_components.keys()).index(item[0]))

        temp_graph_subcomponent = get_subcomponent_outer_ring(item[0],
                                                              query_results,
                                                              uat_type,
                                                              frame_components)
        priority_total['total'] += item[3]  # Total number of all issues of pie chart table
        temp_table.append(item[0])

        # Number of issues Open, Resolved, Closed
        for status in ISSUE_STATUS_FIELDS:
            for i in status[1]:
                priority_total[status[0]] += item[i]
                temp_table.append(float(item[i]))

        temp_table.append(None)
        temp_table.append(float(item[3]))  # SubTotal of pie chart table

        dd_pie_table.append(temp_table)
        donut_pie_inner.append(temp_graph)
        donut_pie_outer.append(temp_graph_subcomponent)

    dd_pie_table_subcomponent = []  # calculate issues count per sub component

    for item in sorted(frame_components.keys()):
        temp_table = []

        try:
            if item not in list(zip(*weight_factor)[0]):
                temp_table.append(item)
                for status in ISSUE_STATUS_FIELDS:
                    for i in status[1]:
                        temp_table.append(0)
                temp_table.append(None)
                temp_table.append(0)

                dd_pie_table.append(temp_table)

        except IndexError:
            continue

        for each in data_issue_counts:
            temp_table_subcomponent = []
            sub_total = 0

            if each.startswith(item + '/'):
                temp_table_subcomponent.append(each[len(item) + 1:])
                for status in ISSUE_STATUS_FIELDS:
                    temp_table_subcomponent.append(float(data_issue_counts[each][status[0]]['open']))
                    temp_table_subcomponent.append(float(data_issue_counts[each][status[0]]['resolved']))
                    temp_table_subcomponent.append(float(data_issue_counts[each][status[0]]['closed']))
                    sub_total += sum(data_issue_counts[each][status[0]].itervalues())
            else:
                continue

            if sub_total == 0:
                continue
            else:
                temp_table_subcomponent.append(None)
                temp_table_subcomponent.append(sub_total)

            dd_pie_table_subcomponent.append(temp_table_subcomponent)

    temp_table = []
    temp_table.append('Total')
    temp_table.append(None)
    for status in ISSUE_STATUS_FIELDS:  #  total number per priority
        temp_table.append(priority_total[status[0]])
        temp_table.append(None)
        temp_table.append(None)
    temp_table.append(priority_total['total'])

    dd_pie_graph.append(donut_pie_inner)
    dd_pie_graph.append(donut_pie_outer)

    dd_pie_data.append(dd_pie_graph)

    # Sub components issue counts sorted by subtotal
    dd_pie_data.append(sorted(dd_pie_table_subcomponent, key=itemgetter(17), reverse=True))

    dd_pie_data.append(temp_table)
    dd_pie_data.append(uat_score)

    return dd_pie_data


def get_subcomponent_outer_ring(component_name, query_results, uat_type, frame_components):
    sub_component_names = []
    component_name_list = []
    sub_pie_graph = []

    component_name_weight = Decimal(round(frame_components[component_name] / Decimal(20), 3))
    component_name_list.append(component_name)

    for item in query_results:
        if item['components'] and item['components'].startswith(component_name):
            sub_component_names.append(item['components'])

    sub_component_names = list(OrderedDict.fromkeys(sub_component_names))
    sub_component_names_length = Decimal(len(sub_component_names))

    data = issue_counts_compute(sub_component_names,
                                component_name_list,
                                query_results,
                                'sub_components',
                                uat_type)
    weight_factor = get_subcomponent_weight_factor(data, component_name, component_name_weight)

    for item in data:
        temp_graph = []
        if item == component_name:
            continue

        temp_graph.append(item[len(component_name) + 1:])
        temp_graph.append(float(sum(data[item]['ceeq'].itervalues())))

        sub_pie_graph.append(temp_graph)

    return sub_pie_graph


def get_subcomponent_weight_factor(data, component_name, component_name_weight):
    for item in data:
        for status in ISSUE_STATUS_COUNT.keys():
            data[item]['total'][status] = data[item]['blocker'][status] \
                                          + data[item]['critical'][status]\
                                          + data[item]['major'][status]\
                                          + data[item]['minor'][status]\
                                          + data[item]['trivial'][status]
    sub_component_names_length = 0
    for item in data:
        if item.startswith(component_name + '/') and sum(data[item]['total'].itervalues()) > 0:
            sub_component_names_length += 1
        else:
            continue

    for item in data:
        for status in ISSUE_STATUS_COUNT.keys():
            if sub_component_names_length == 0:
                continue
            data[item]['ceeq'][status] = data[item]['blocker'][status] * ISSUE_STATUS_WEIGHT[status] * ISSUE_PRIORITY_WEIGHT['blocker'] / sub_component_names_length * component_name_weight \
                                         + data[item]['critical'][status] * ISSUE_STATUS_WEIGHT[status] * ISSUE_PRIORITY_WEIGHT['critical'] / sub_component_names_length * component_name_weight \
                                         + data[item]['major'][status] * ISSUE_STATUS_WEIGHT[status] * ISSUE_PRIORITY_WEIGHT['major'] / sub_component_names_length * component_name_weight \
                                         + data[item]['minor'][status] * ISSUE_STATUS_WEIGHT[status] * ISSUE_PRIORITY_WEIGHT['minor'] / sub_component_names_length * component_name_weight \
                                         + data[item]['trivial'][status] * ISSUE_STATUS_WEIGHT[status] * ISSUE_PRIORITY_WEIGHT['trivial'] / sub_component_names_length * component_name_weight

    return data


def get_ceeq_trend_graph(project, uat_type):
    """
    Get Ceeq score history records from ScoreHistory table
    :param project:
    :param uat_type:
    :return: Categories(date), Actual ceeq score, and Projected ceeq score
    """
    # results = project.resulthistory_set.all()
    # last_per_day = results.extra(select={'the_date': 'date(confirmed)'}).values_list('the_date').annotate(max_date=Max('confirmed'))
    # max_dates = [item[1] for item in last_per_day]
    # results_per_day = ResultHistory.objects.filter(confirmed__in=max_dates).order_by('confirmed')

    score_history = project.scorehistory_set.all().order_by('created')

    data = {}
    categories = []
    data_ceeq = []
    data_ceeq_closed = []
    for item in score_history:
        if not item.combined_score or not item.internal_score or not item.uat_score:
            continue
        if item.created.month < 10:
            tmp_month = '0' + str(item.created.month)
        else:
            tmp_month = str(item.created.month)

        if item.created.day < 10:
            tmp_day = '0' + str(item.created.day)
        else:
            tmp_day = str(item.created.day)
        tmp_year = str(item.created.year)

        categories.append(tmp_year + '-' + tmp_month + '-' + tmp_day)

        if uat_type == 'include_uat':
            data_ceeq.append(float(item.combined_score[0]))
            data_ceeq_closed.append(float(item.combined_score[1]))
        elif uat_type == 'exclude_uat':
            data_ceeq.append(float(item.internal_score[0]))
            data_ceeq_closed.append(float(item.internal_score[1]))
        elif uat_type == 'only_uat':
            data_ceeq.append(float(item.uat_score[0]))
            data_ceeq_closed.append(float(item.uat_score[1]))

    data['categories'] = categories
    data['ceeq'] = data_ceeq
    data['ceeq_closed'] = data_ceeq_closed

    return data


def update_score_history(project_id, combined_score, internal_score, uat_score):
    """
    Update CEEQ score per project per day
    :param project_id:
    :param combined_score:
    :param internal_score:
    :param uat_score:
    :return: None
    """
    project = get_object_or_404(Project, pk=project_id)
    today = datetime.today().date()
    try:
        access = project.scorehistory_set.latest('created')
        if access.created.date() == today:
            access.combined_score = combined_score
            access.internal_score = internal_score
            access.uat_score = uat_score
            access.save()
        else:
            access = ScoreHistory.objects.create(project=project)
            access.combined_score = combined_score
            access.internal_score = internal_score
            access.uat_score = uat_score
            access.save()
    except ScoreHistory.DoesNotExist:
        access = ScoreHistory.objects.create(project=project)
        access.combined_score = combined_score
        access.internal_score = internal_score
        access.uat_score = uat_score
        access.save()


def fetch_subcomponents_pie(project_id, component_name, uat_type, start, end, uat_type_custom):
    project = get_object_or_404(Project, pk=project_id)
    result_latest = project.resulthistory_set.latest('confirmed')
    query_results = result_latest.query_results

    # get custom data from query results
    query_results_custom = []
    if uat_type == 'custom':
        start_date = datetime.fromtimestamp(int(start)).strftime('%Y-%m-%d')
        end_date = datetime.fromtimestamp(int(end)).strftime('%Y-%m-%d')

        for item in query_results:
            if start_date <= item['created'] <= end_date:
                query_results_custom.append(item)

        query_results = query_results_custom

    sub_component_names = []
    for item in query_results:
        if item['components'].startswith(component_name[0]):
            sub_component_names.append(item['components'])
    sub_component_names = list(OrderedDict.fromkeys(sub_component_names))

    if uat_type == 'custome':
        data = issue_counts_compute(sub_component_names,
                                    component_name,
                                    query_results,
                                    'sub_components',
                                    uat_type_custom)
    else:
        data = issue_counts_compute(sub_component_names,
                                    component_name,
                                    query_results,
                                    'sub_components',
                                    uat_type)

    sub_weight_factor = get_subcomponent_weight_factor(data, component_name[0], 1)

    priority_total = defaultdict(int)
    sub_pie_data = []
    sub_pie_table = []
    sub_pie_graph = []

    for item in data:
        if item == component_name[0] or sum(data[item]['total'].itervalues()) == 0:
            continue
        tmp_graph = []
        tmp_table = []
        sub_total = 0

        priority_total['total'] += sum(data[item]['total'].itervalues())

        tmp_graph.append(item[len(component_name[0]) + 1:])
        tmp_graph.append(float(sum(data[item]['ceeq'].itervalues())))

        tmp_table.append(item[len(component_name[0]) + 1:])
        for status in ISSUE_STATUS_FIELDS:
            tmp_table.append(float(data[item][status[0]]['open']))
            tmp_table.append(float(data[item][status[0]]['resolved']))
            tmp_table.append(float(data[item][status[0]]['closed']))

            sub_total += sum(data[item][status[0]].itervalues())

            priority_total[status[0]] += sum(data[item][status[0]].itervalues())

        tmp_table.append(None)
        tmp_table.append(sub_total)

        sub_pie_graph.append(tmp_graph)
        sub_pie_table.append(tmp_table)

    tmp_table = []
    tmp_table.append('Total')
    tmp_table.append(None)
    for status in ISSUE_STATUS_FIELDS:
        tmp_table.append(priority_total[status[0]])
        tmp_table.append(None)
        tmp_table.append(None)
    tmp_table.append(priority_total['total'])

    sub_pie_data.append(sub_pie_graph)
    sub_pie_data.append(sub_pie_table)
    sub_pie_data.append(tmp_table)

    return sub_pie_data


