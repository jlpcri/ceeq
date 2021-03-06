from collections import OrderedDict, defaultdict
import copy
from decimal import Decimal
from django.shortcuts import get_object_or_404
from ceeq.apps.projects.models import FrameworkParameter, Project, ProjectComponentsDefectsDensity, ProjectType
from django.conf import settings

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
    if string and '/' in string:
        index = string.index('/')
        return string[:index]
    else:
        return string


def remove_period_space(string):
    special_chars = [' ', '.', ',', '/']
    for ch in special_chars:
        if ch in string:
            string = string.replace(ch, '_')

    return string


def get_weight_factor(data, component_names_without_slash_all, frame_components):
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
                                     if component in frame_components]

    for component in component_names_without_slash:
        for item in data:
            if item.startswith(component+'/'):
                for status in settings.ISSUE_STATUS_COUNT.keys():
                    # total number of jiras per sub component
                    data[item]['total'][status] = data[item]['blocker'][status] \
                                        + data[item]['critical'][status] \
                                        + data[item]['major'][status] \
                                        + data[item]['minor'][status] \
                                        + data[item]['trivial'][status]

                    # defects density per sub component
                    data[item]['ceeq'][status] = data[item]['blocker'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['blocker'] * jira_issue_weight_sum\
                                        + data[item]['critical'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['critical'] * jira_issue_weight_sum\
                                        + data[item]['major'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['major'] * jira_issue_weight_sum\
                                        + data[item]['minor'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['minor'] * jira_issue_weight_sum\
                                        + data[item]['trivial'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['trivial'] * jira_issue_weight_sum

                    # defects density per sub component if all closed
                    data[item]['ceeq_closed'][status] = data[item]['blocker'][status] * settings.ISSUE_STATUS_WEIGHT['closed'] * settings.ISSUE_PRIORITY_WEIGHT['blocker'] * jira_issue_weight_sum\
                                        + data[item]['critical'][status] * settings.ISSUE_STATUS_WEIGHT['closed'] * settings.ISSUE_PRIORITY_WEIGHT['critical'] * jira_issue_weight_sum\
                                        + data[item]['major'][status] * settings.ISSUE_STATUS_WEIGHT['closed'] * settings.ISSUE_PRIORITY_WEIGHT['major'] * jira_issue_weight_sum\
                                        + data[item]['minor'][status] * settings.ISSUE_STATUS_WEIGHT['closed'] * settings.ISSUE_PRIORITY_WEIGHT['minor'] * jira_issue_weight_sum\
                                        + data[item]['trivial'][status] * settings.ISSUE_STATUS_WEIGHT['closed'] * settings.ISSUE_PRIORITY_WEIGHT['trivial'] * jira_issue_weight_sum

                    data[component]['blocker'][status] += data[item]['blocker'][status]
                    data[component]['critical'][status] += data[item]['critical'][status]
                    data[component]['major'][status] += data[item]['major'][status]
                    data[component]['minor'][status] += data[item]['minor'][status]
                    data[component]['trivial'][status] += data[item]['trivial'][status]

                    data[component]['total'][status] += data[item]['total'][status]

    # for i in data:
    #     print i, data[i]['ceeq'], data[i]['ceeq_closed']

    #calculate defect density of each component
    for component in component_names_without_slash:
        #for status in settings.ISSUE_STATUS_COUNT.keys():
        #    try:
        #        issue_status_weight_base += issue_status_weight[status]
        #    except KeyError:
        #        continue

        for item in data:
            if item.startswith(component + '/'):
                for status in settings.ISSUE_STATUS_COUNT.keys():
                    data[component]['ceeq'][status] += data[item]['ceeq'][status]
                    data[component]['ceeq_closed'][status] += data[item]['ceeq_closed'][status]

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
            # for status in settings.ISSUE_STATUS_COUNT.keys():
            #     # total number of jiras per sub component
            #     data[component]['total'][status] = data[component]['blocker'][status] \
            #                         + data[component]['critical'][status] \
            #                         + data[component]['major'][status] \
            #                         + data[component]['minor'][status] \
            #                         + data[component]['trivial'][status]
            #
            #     # defects density per sub component
            #     data[component]['ceeq'][status] = data[component]['blocker'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['blocker']\
            #                         + data[component]['critical'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['critical']\
            #                         + data[component]['major'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['major']\
            #                         + data[component]['minor'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['minor']\
            #                         + data[component]['trivial'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['trivial']

            continue
        else:
            for status in settings.ISSUE_STATUS_WEIGHT.keys():
                data[component]['ceeq'][status] /= subcomponent_length
                data[component]['ceeq_closed'][status] /= subcomponent_length

    weight_factor = []
    weight_factor_base = 20

    """
    -------Dynamic change weight ration-------
    for item in component_names_without_slash:
        try:
            # Skip the component with zero issues
            if sum(data[item]['total'].itervalues()) == 0:
                continue
            weight_factor_base += settings.COMPONENT_NAMES_STANDARD[item]
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
            temp.append(round(frame_components[item] / float(weight_factor_base), 3))
        except KeyError:
            continue

        temp.append(sum(data[item]['ceeq'].itervalues()))  # defect density, decimal
        temp.append(sum(data[item]['total'].itervalues()))  # total number per component

        for priority in sorted(settings.ISSUE_PRIORITY_WEIGHT.keys()):
            for status in sorted(settings.ISSUE_STATUS_COUNT.keys()):
                try:
                    temp.append(data[item][priority][status])
                except KeyError:
                    continue

        temp.append(sum(data[item]['ceeq_closed'].itervalues()))
        weight_factor.append(temp)

    # print weight_factor
    return weight_factor


def issue_counts_compute(request, component_names, component_names_without_slash, jira_data, component_type, uat_type, frame_components):
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
        'ceeq': settings.ISSUE_STATUS_COUNT.copy(),  # store ceeq score
        'total': settings.ISSUE_STATUS_COUNT.copy(),  # total number of jira per component/sub component
        'blocker': settings.ISSUE_STATUS_COUNT.copy(),
        'critical': settings.ISSUE_STATUS_COUNT.copy(),
        'major': settings.ISSUE_STATUS_COUNT.copy(),
        'minor': settings.ISSUE_STATUS_COUNT.copy(),
        'trivial': settings.ISSUE_STATUS_COUNT.copy(),
        'ceeq_closed': settings.ISSUE_STATUS_COUNT.copy()  # for if all JIRAs are closed
    }

    #print 'aaa: ', component_names
    #print 'bbb: ', component_names_without_slash
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
        if uat_type == 'include_uat':
            pass
        elif uat_type == 'exclude_uat':
            # UAT workflow metatype not counted
            if item['fields']['customfield_13286']:
                continue
        elif uat_type == 'only_uat':
            # Only workflow metatype counted
            if item['fields']['customfield_13286'] is None:
                continue

        # Closed type: Works as Designed not counted
        if item['fields']['resolution'] \
                and item['fields']['resolution']['id'] in settings.ISSUE_RESOLUTION_NOT_COUNT\
                and item['fields']['status']['id'] in settings.ISSUE_STATUS_CLOSED:
            continue

        # TFCC Is Root Cause - customfield_10092 not counted
        try:
            if item['fields']['resolution']\
                    and item['fields']['resolution']['id'] in settings.ISSUE_RESOLUTION_EXTERNAL_LIMITATION \
                    and item['fields']['customfield_10092']['id'] in settings.ISSUE_TFCC_IS_ROOT_CAUSE \
                    and item['fields']['status']['id'] in settings.ISSUE_STATUS_CLOSED:
                continue
        except (KeyError, TypeError):
            continue

        # if first item-component is not in framework, then check next, until end
        component_len = len(item['fields']['components'])
        if component_len == 0:
            continue
        else:
            component = get_component_names_from_jira_data(component_len, item['fields']['components'], frame_components)

        # if return component is None, then continue to next
        if not component:
            continue

        if component_type == 'sub_components' and not component.startswith(component_names_without_slash[0]):
            continue

        if item['fields']['issuetype']['id'] in issue_types:
            if item['fields']['status']['id'] in settings.ISSUE_STATUS_OPEN:
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
            elif item['fields']['status']['id'] in settings.ISSUE_STATUS_RESOLVED:
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
            elif item['fields']['status']['id'] in settings.ISSUE_STATUS_CLOSED:
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


def get_subcomponent_defects_density(request, component_name, version_data, uat_type, frame_components):
    sub_component_names = []
    component_name_list = []
    sub_pie_graph = []

    component_name_weight = Decimal(round(frame_components[component_name] / Decimal(20), 3))
    component_name_list.append(component_name)

    for item in version_data:
        # if first item-component is not in framework, then check next, until end
        component_len = len(item['fields']['components'])
        if component_len == 0:
            continue
        else:
            name = get_component_names_from_jira_data(component_len, item['fields']['components'], frame_components)

        if name and name.startswith(component_name):
            sub_component_names.append(name)

    sub_component_names = list(OrderedDict.fromkeys(sub_component_names))
    sub_component_names_length = Decimal(len(sub_component_names))

    data = issue_counts_compute(request,
                                sub_component_names,
                                component_name_list,
                                version_data,
                                'sub_components',
                                uat_type,
                                frame_components)

    weight_factor = get_sub_component_weight_factor(data, component_name, component_name_weight)

    for item in data:
        temp_graph = []

        if item == component_name:
            continue

        temp_graph.append(item[len(component_name) + 1:])
        temp_graph.append(float(sum(data[item]['ceeq'].itervalues())))
        #print temp_graph

        sub_pie_graph.append(temp_graph)

    #print sub_pie_graph

    return sub_pie_graph


def get_sub_component_weight_factor(data, component_name, component_name_weight):
    for item in data:
        for status in settings.ISSUE_STATUS_COUNT.keys():
            # total number of jiras per sub component
            data[item]['total'][status] = data[item]['blocker'][status] \
                                        + data[item]['critical'][status] \
                                        + data[item]['major'][status] \
                                        + data[item]['minor'][status] \
                                        + data[item]['trivial'][status]

    sub_component_names_length = 0
    for item in data:
        #if item == 'Voice Prompts' and sum(data[item]['total'].itervalues()) > 0:
        #    sub_component_names_length = 1
        #    break
        if item.startswith(component_name+'/') and sum(data[item]['total'].itervalues()) > 0:
            sub_component_names_length += 1
        else:
            continue

    for item in data:
        for status in settings.ISSUE_STATUS_COUNT.keys():
            if sub_component_names_length == 0:
                continue
            # defects density per sub component
            data[item]['ceeq'][status] = data[item]['blocker'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['blocker'] / sub_component_names_length * component_name_weight \
                                + data[item]['critical'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['critical'] / sub_component_names_length * component_name_weight \
                                + data[item]['major'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['major'] / sub_component_names_length * component_name_weight \
                                + data[item]['minor'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['minor'] / sub_component_names_length * component_name_weight \
                                + data[item]['trivial'][status] * settings.ISSUE_STATUS_WEIGHT[status] * settings.ISSUE_PRIORITY_WEIGHT['trivial'] / sub_component_names_length * component_name_weight

    return data


def get_priority_total(weight_factor):
    priority_total = defaultdict(int)

    for item in weight_factor:
        #print item
        priority_total['total'] += item[3]
        for status in settings.ISSUE_STATUS_FIELDS:
            priority_total[status[0]] += sum(item[i] for i in status[1])

    return priority_total


def get_component_names(weight_factor):
    try:
        component_names_exist = list(zip(*weight_factor)[0])
    except IndexError:
        component_names_exist = None

    return component_names_exist


def get_component_names_from_jira_data(component_len, components, frame_components):
    # if first item-component is not in framework, then check next, until end
    for i in range(component_len):
        try:
            component = str(components[i]['name'])
        except UnicodeEncodeError:
            component = ''.join(components[i]['name']).encode('utf-8').strip()
            component = component.decode('utf-8')
        if component.startswith(tuple(frame_components.keys())):
            return component
        else:
            continue

    return None


def fetch_ceeq_trend_graph(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project_dds = ProjectComponentsDefectsDensity.objects.filter(project=project)

    data = {}
    categories = []
    data_ceeq = []
    data_ceeq_closed = []

    for item in project_dds:
        if item.version == project.jira_version:
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
            data_ceeq.append(float(item.ceeq))
            data_ceeq_closed.append(float(item.ceeq_closed))

    data['categories'] = categories
    data['ceeq'] = data_ceeq
    data['ceeq_closed'] = data_ceeq_closed

    return data


#  define global variable of project types
def get_project_types():
    project_types = []
    for item in ProjectType.objects.all():
        temp = {
            'name': item.name,
            'value': item.pk
        }
        project_types.append(temp)

    return project_types
