from collections import OrderedDict
from decimal import Decimal
from ceeq.apps.projects.models import FrameworkParameter
from ceeq.settings.base import component_names_standard, issue_status_count, issue_status_weight, issue_priority_weight

__author__ = 'sliu'
"""
 Methods used for abstraction, code duplicatoin
"""


def project_detail_calculate_score(weight_factor):
    raw_score = 0
    for item in weight_factor:
        raw_score += Decimal(item[1]) * item[2]  # item[1]: component weight, float, item[2]: defects density, decimal
    raw_score = (1 - raw_score) * 10  # projects score = 10 - defect score

    if raw_score < 0:  # projects score out of range (0-10)
        score = 20
    elif raw_score == 10:  # no open issues in JIRA
        score = -3
    else:
        score = round(raw_score, 2)

    return score


def version_name_from_jira_data(jira_data):
    version_names = []
    for item in jira_data['issues']:
        try:
            name = str(item['fields']['versions'][0]['name'])
        except (IndexError, UnicodeEncodeError):
            continue
        version_names.append(name)

    version_names = list(OrderedDict.fromkeys(version_names))

    version_names = sorted(version_names)

    return version_names


def truncate_after_slash(string):
    if '/' in string:
        index = string.index('/')
        return string[:index]
    else:
        return string


def remove_period_space(str):
    tmp = str.replace('.', '_')
    tmp = tmp.replace(' ', '_')
    tmp = tmp.replace(',', '_')
    return tmp


def get_weight_factor(data, component_names_without_slash_all):
    """
    calculate issues number of components and sub-components

    :param data: jira_data
    :param component_names_without_slash_all: exclude sub components
    :return: weight_factor: component name, weight, defect density, total number,
                            blocker(Closed, Open, Resolved)
                            ...
                            trivial(Closed, Open, Resolved)
    """

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

    # remove items not in standard
    component_names_without_slash = [component
                                     for component in component_names_without_slash_all
                                     if component in component_names_standard]

    for component in component_names_without_slash:
        for item in data:
            if item.startswith(component+'/'):
                for status in issue_status_count.keys():
                    # total number of jiras per sub component
                    data[item]['total'][status] = data[item]['blocker'][status] \
                                        + data[item]['critical'][status] \
                                        + data[item]['major'][status] \
                                        + data[item]['minor'][status] \
                                        + data[item]['trivial'][status]

                    # defects density per sub component
                    data[item]['ceeq'][status] = data[item]['blocker'][status] * issue_status_weight[status] * issue_priority_weight['blocker'] * jira_issue_weight_sum\
                                        + data[item]['critical'][status] * issue_status_weight[status] * issue_priority_weight['critical'] * jira_issue_weight_sum\
                                        + data[item]['major'][status] * issue_status_weight[status] * issue_priority_weight['major'] * jira_issue_weight_sum\
                                        + data[item]['minor'][status] * issue_status_weight[status] * issue_priority_weight['minor'] * jira_issue_weight_sum\
                                        + data[item]['trivial'][status] * issue_status_weight[status] * issue_priority_weight['trivial'] * jira_issue_weight_sum

                    data[component]['blocker'][status] += data[item]['blocker'][status]
                    data[component]['critical'][status] += data[item]['critical'][status]
                    data[component]['major'][status] += data[item]['major'][status]
                    data[component]['minor'][status] += data[item]['minor'][status]
                    data[component]['trivial'][status] += data[item]['trivial'][status]

                    data[component]['total'][status] += data[item]['total'][status]

    #issue_status_weight_base = 10

    #calculate defect density of each component
    for component in component_names_without_slash:
        #for status in issue_status_count.keys():
        #    try:
        #        issue_status_weight_base += issue_status_weight[status]
        #    except KeyError:
        #        continue

        for item in data:
            if item.startswith(component + '/'):
                for status in issue_status_count.keys():
                    data[component]['ceeq'][status] += data[item]['ceeq'][status]

    #formalize total sum of each component by divided by number of sub-components
    for component in component_names_without_slash:
        subcomponent_length = 0
        for item in data:
            #if sub component has zero issue then skip
            if item.startswith(component+'/') and sum(data[item]['ceeq'].itervalues()) > 0:
                subcomponent_length += 1
            else:
                continue
        if subcomponent_length == 0:
            # component which does not have sub component
            for status in issue_status_count.keys():
                # total number of jiras per sub component
                data[component]['total'][status] = data[component]['blocker'][status] \
                                    + data[component]['critical'][status] \
                                    + data[component]['major'][status] \
                                    + data[component]['minor'][status] \
                                    + data[component]['trivial'][status]

                # defects density per sub component
                data[component]['ceeq'][status] = data[component]['blocker'][status] * issue_status_weight[status] * issue_priority_weight['blocker']\
                                    + data[component]['critical'][status] * issue_status_weight[status] * issue_priority_weight['critical']\
                                    + data[component]['major'][status] * issue_status_weight[status] * issue_priority_weight['major']\
                                    + data[component]['minor'][status] * issue_status_weight[status] * issue_priority_weight['minor']\
                                    + data[component]['trivial'][status] * issue_status_weight[status] * issue_priority_weight['trivial']

            continue
        else:
            for status in issue_status_weight.keys():
                data[component]['ceeq'][status] /= subcomponent_length

    weight_factor = []
    weight_factor_base = 20

    """
    -------Dynamic change weight ration-------
    for item in component_names_without_slash:
        try:
            # Skip the component with zero issues
            if sum(data[item]['total'].itervalues()) == 0:
                continue
            weight_factor_base += component_names_standard[item]
        except KeyError:
            continue
    """

    for item in sorted(component_names_without_slash):
        temp = []
        # Skip the component with zero issues
        if sum(data[item]['total'].itervalues()) == 0:
            continue
        temp.append(item)   # component name
        try:
            # dynamic component weight, float
            temp.append(round(component_names_standard[item] / float(weight_factor_base), 3))
        except KeyError:
            continue

        temp.append(sum(data[item]['ceeq'].itervalues()))  # defect density, decimal
        temp.append(sum(data[item]['total'].itervalues()))  # total number per component

        for priority in sorted(issue_priority_weight.keys()):
            for status in sorted(issue_status_count.keys()):
                try:
                    temp.append(data[item][priority][status])
                except KeyError:
                    continue

        weight_factor.append(temp)

    return weight_factor

