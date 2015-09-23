from collections import OrderedDict
import copy
from decimal import Decimal

from ceeq.apps.calculator.models import SeverityMap, LiveSettings, ComponentImpact

# define globe variables
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


def get_table_data(query_results, uat_type):
    print 'table: ', uat_type
    print query_results


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
    data['score'] = score
    data['weight_factor'] = weight_factor


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
            if item['customfield_13286']:
                continue
        elif uat_type == 'only_uat':
            # Only workflow metatype counted
            if not item['customfield_13286']:
                continue

        component = item['components']
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
    raw_score = 0
    for item in weight_factor:
        raw_score += Decimal(item[1] * item[2])  # item[1]: component weight, float, item[2]: defects density, decimal
    raw_score = (1 - raw_score) * 10

    if raw_score == 10:  # no open issues in JIRA
        score = 103
    else:
        score = round(raw_score, 2)

    return score

