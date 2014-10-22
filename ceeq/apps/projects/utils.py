from collections import OrderedDict
import copy
from decimal import Decimal
from ceeq.apps.projects.models import FrameworkParameter
from ceeq.settings.base import component_names_standard, issue_status_count, issue_status_weight, issue_priority_weight, \
    issue_status_open, issue_status_resolved, issue_status_closed, issue_resolution_not_count

"""
 Methods used for abstraction, code duplicatoin
"""


def project_detail_calculate_score(weight_factor):
    raw_score = 0
    for item in weight_factor:
        raw_score += Decimal(item[1]) * item[2]  # item[1]: component weight, float, item[2]: defects density, decimal
    raw_score = (1 - raw_score) * 10  # projects score = 10 - defect score

    #print round(raw_score, 2)
    if raw_score < 0:  # projects score out of range (0-10)
        #score = 20
        score = round(raw_score, 2)
    elif raw_score == 10:  # no open issues in JIRA
        score = 103
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


def issue_counts_compute(request, component_names, component_names_without_slash, jira_data, component_type):
    """
    Compute number of issues Component, SubComponent, Priority, Status
    :param request:
    :param component_names: include SubComponents
    :param component_names_without_slash: without SubComponents
    :param jira_data: raw data from JIRA
    :param component_type: calculate based on Components or SubComponents
    :return: dictionary data
    """
    data = {}
    issue_counts = {
        'ceeq': issue_status_count.copy(),  # store ceeq score
        'total': issue_status_count.copy(),  # total number of jira per component/sub component
        'blocker': issue_status_count.copy(),
        'critical': issue_status_count.copy(),
        'major': issue_status_count.copy(),
        'minor': issue_status_count.copy(),
        'trivial': issue_status_count.copy()
    }

    for item in component_names:
        data[item] = copy.deepcopy(issue_counts)  # copy the dict object

    for item in component_names_without_slash:  # add component item to data
        if item in data.keys():
            continue
        else:
            data[item] = copy.deepcopy(issue_counts)

    #construct isstype filter
    # 1-Bug, 2-New Feature, 3-Task, 4-Improvement
    issue_types = ['1']
    if request:  # daily_dd_log: request=None
        if request.user.usersettings.new_feature:
            issue_types.append('2')
        if request.user.usersettings.task:
            issue_types.append('3')
        if request.user.usersettings.improvement:
            issue_types.append('4')
        if request.user.usersettings.suggested_improvement:
            issue_types.append('15')
        if request.user.usersettings.environment:
            issue_types.append('17')

    for item in jira_data:
        # Closed type: Works as Designed not counted
        if item['fields']['resolution'] and item['fields']['resolution']['id'] in issue_resolution_not_count:
            continue

        try:
            component = item['fields']['components'][0]['name']
        except (IndexError, UnicodeEncodeError):
            continue

        #print 'a', component
        if component_type == 'sub_components' and not component.startswith(component_names_without_slash[0]):
            continue

        if item['fields']['issuetype']['id'] in issue_types:
            if item['fields']['status']['id'] in issue_status_open:
                if item['fields']['priority']['id'] == '1':
                    data[component]['blocker']['open'] += 1
                elif item['fields']['priority']['id'] == '2':
                    data[component]['critical']['open'] += 1
                elif item['fields']['priority']['id'] == '3':
                    data[component]['major']['open'] += 1
                elif item['fields']['priority']['id'] == '4':
                    data[component]['minor']['open'] += 1
                elif item['fields']['priority']['id'] == '5':
                    data[component]['trivial']['open'] += 1
            elif item['fields']['status']['id'] in issue_status_resolved:
                #TODO: Track time usage of Resolved JIRAs
                """
                print item['fields']['created'], ',', item['fields']['resolutiondate']
                difference = datetime.strptime(item['fields']['resolutiondate'][:19], '%Y-%m-%dT%H:%M:%S') - datetime.strptime(item['fields']['created'][:19], '%Y-%m-%dT%H:%M:%S')
                print 'hours: ', divmod(difference.total_seconds(), 3600)[0]
                """
                if item['fields']['priority']['id'] == '1':
                    data[component]['blocker']['resolved'] += 1
                elif item['fields']['priority']['id'] == '2':
                    data[component]['critical']['resolved'] += 1
                elif item['fields']['priority']['id'] == '3':
                    data[component]['major']['resolved'] += 1
                elif item['fields']['priority']['id'] == '4':
                    data[component]['minor']['resolved'] += 1
                elif item['fields']['priority']['id'] == '5':
                    data[component]['trivial']['resolved'] += 1
            elif item['fields']['status']['id'] in issue_status_closed:
                #print 'C', item['fields']['created'], item['fields']['resolutiondate']
                if item['fields']['priority']['id'] == '1':
                    data[component]['blocker']['closed'] += 1
                elif item['fields']['priority']['id'] == '2':
                    data[component]['critical']['closed'] += 1
                elif item['fields']['priority']['id'] == '3':
                    data[component]['major']['closed'] += 1
                elif item['fields']['priority']['id'] == '4':
                    data[component]['minor']['closed'] += 1
                elif item['fields']['priority']['id'] == '5':
                    data[component]['trivial']['closed'] += 1



    #for i in data:
    #    print i, data[i]

    return data


def get_subcomponent_defects_density(request, component_name, version_data):
    sub_component_names = []
    component_name_list = []
    sub_pie_graph = []

    component_name_weight = Decimal(round(component_names_standard[component_name] / Decimal(20), 3))
    component_name_list.append(component_name)

    for item in version_data:
        try:
            name = str(item['fields']['components'][0]['name'])
        except (IndexError, UnicodeEncodeError):
            continue
        if name.startswith(component_name):
            sub_component_names.append(name)

    sub_component_names = list(OrderedDict.fromkeys(sub_component_names))
    sub_component_names_length = Decimal(len(sub_component_names))

    data = issue_counts_compute(request, sub_component_names, component_name_list, version_data, 'sub_components')

    weight_factor = get_sub_component_weight_factor(data, component_name, component_name_weight)

    for item in data:
        temp_graph = []

        if item == component_name and item != 'Voice Slots':
            continue

        if item != 'Voice Slots':
            temp_graph.append(item[len(component_name) + 1:])
        else:
            temp_graph.append(item)
        temp_graph.append(float(sum(data[item]['ceeq'].itervalues())))
        #print temp_graph

        sub_pie_graph.append(temp_graph)

    #print sub_pie_graph

    return sub_pie_graph


def get_sub_component_weight_factor(data, component_name, component_name_weight):
    for item in data:
        for status in issue_status_count.keys():
            # total number of jiras per sub component
            data[item]['total'][status] = data[item]['blocker'][status] \
                                        + data[item]['critical'][status] \
                                        + data[item]['major'][status] \
                                        + data[item]['minor'][status] \
                                        + data[item]['trivial'][status]

    sub_component_names_length = 0
    for item in data:
        if item == 'Voice Slots' and sum(data[item]['total'].itervalues()) > 0:
            sub_component_names_length = 1
            break
        elif item.startswith(component_name+'/') and sum(data[item]['total'].itervalues()) > 0:
            sub_component_names_length += 1
        else:
            continue

    for item in data:
        for status in issue_status_count.keys():
            # defects density per sub component
            data[item]['ceeq'][status] = data[item]['blocker'][status] * issue_status_weight[status] * issue_priority_weight['blocker'] / sub_component_names_length * component_name_weight \
                                + data[item]['critical'][status] * issue_status_weight[status] * issue_priority_weight['critical'] / sub_component_names_length * component_name_weight \
                                + data[item]['major'][status] * issue_status_weight[status] * issue_priority_weight['major'] / sub_component_names_length * component_name_weight \
                                + data[item]['minor'][status] * issue_status_weight[status] * issue_priority_weight['minor'] / sub_component_names_length * component_name_weight \
                                + data[item]['trivial'][status] * issue_status_weight[status] * issue_priority_weight['trivial'] / sub_component_names_length * component_name_weight

    return data