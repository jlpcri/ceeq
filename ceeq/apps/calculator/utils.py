from collections import OrderedDict
import copy
from django.conf import settings

__author__ = 'sliu'


def get_table_data(query_results, uat_type):
    print 'table: ', uat_type
    print query_results


def get_score_data(project, query_results, component_names_standard, uat_type):
    # for item in query_results:
    #     print item
    print len(query_results)
    component_names = []
    component_names_without_slash = []

    for item in query_results:
        component_names.append(item['components'])
        component_names_without_slash.append(truncate_after_slash(item['components']))

    component_names = list(OrderedDict.fromkeys(component_names))
    component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

    print component_names
    print component_names_without_slash

    # calculate issue counts
    data_issue_counts = issue_counts_compute(project,
                                             component_names,
                                             component_names_without_slash,
                                             query_results,
                                             'components',  # calculation for Components or Sub Components
                                             uat_type)

    # weight_factor = get_weight_factor(data_issue_counts, component_names_without_slash)


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


def issue_counts_compute(project, component_names, component_names_without_slash, jira_data, component_type, uat_type):
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
        'ceeq': settings.ISSUE_STATUS_COUNT.copy(),  # store ceeq score
        'total': settings.ISSUE_STATUS_COUNT.copy(),  # total number of jira per component/sub component
        'blocker': settings.ISSUE_STATUS_COUNT.copy(),
        'critical': settings.ISSUE_STATUS_COUNT.copy(),
        'major': settings.ISSUE_STATUS_COUNT.copy(),
        'minor': settings.ISSUE_STATUS_COUNT.copy(),
        'trivial': settings.ISSUE_STATUS_COUNT.copy(),
        'ceeq_closed': settings.ISSUE_STATUS_COUNT.copy()  # for if all JIRAs are closed
    }

    for item in component_names:
        data[item] = copy.deepcopy(issue_counts)  # copy the dict object

    for item in component_names_without_slash:  # add component item to data
        if item in data.keys():
            continue
        else:
            data[item] = copy.deepcopy(issue_counts)

    for item in jira_data:
        # print item
        if uat_type == 'include_uat':
            pass
        elif uat_type == 'exclude_uat':
            # UAT workflow metatype not counted
            if item['customfield_13286']:
                continue
        elif uat_type == 'only_uat':
            # Only workflow metatye counted
            if item['customfield_13286'] is None:
                continue



    # print data
    return data


