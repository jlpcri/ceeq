from ceeq.apps.calculator.models import ImpactMap
from ceeq.apps.queries.models import Instance, Project


#  define global variable of project impact maps
def get_impact_maps():
    impact_maps = []
    for item in ImpactMap.objects.all():
        temp = {
            'name': item.name,
            'value': item.pk
        }
        impact_maps.append(temp)

    return impact_maps


def get_instances():
    instances = []
    for item in Instance.objects.all():
        temp = {
            'url': item.url,
            'value': item.pk
        }
        instances.append(temp)

    return instances


def parse_jira_data(project, component_names_standard):
    results = []
    if project.component_field == Project.COMPONENT:  # use components names
        for issue in project.fetch_jira_data['issues']:
            temp = {}
            temp['key'] = issue['key']
            for item in issue['fields']:
                # check component not in framework continue
                components = issue['fields']['components']
                if len(components) == 1 \
                        and not components[0]['name'].startswith(tuple(component_names_standard)):
                    continue
                if len(components) > 1 \
                        and not get_component_names_per_ticket(len(components), components, component_names_standard):
                    continue
                if len(components) > 1 \
                        and not get_component_names_per_ticket(len(components), components, component_names_standard).startswith(tuple(component_names_standard)):
                    continue

                # Closed and Resolution Blacklist not counted
                if issue['fields']['resolution'] \
                        and issue['fields']['resolution']['name'] in project.resolution_blacklist\
                        and issue['fields']['status']['name'] == 'Closed':
                    continue

                # Only track issue_types
                if issue['fields']['issuetype']['name'] not in project.issue_types:
                    continue

                # TFCC Is Root Cause - customfield_10092 not counted
                try:
                    if issue['fields']['resolution'] \
                            and issue['fields']['resolution']['id'] in ['11']\
                            and issue['fields']['customfield_10092']['id'] in ['13499']:
                        continue
                except (KeyError, TypeError):
                    continue

                # collect data
                if issue['fields'][item]:
                    if item == 'created':
                        temp[item] = issue['fields'][item]
                    elif item in ['customfield_13286', 'customfield_10092']:
                        temp[item] = issue['fields'][item]['value']
                    elif item == 'versions':
                        temp[item] = issue['fields'][item][0]['name']
                    elif item == 'components':
                        if len(issue['fields'][item]) == 1:
                            temp[item] = issue['fields'][item][0]['name']
                        elif len(issue['fields'][item]) > 1:
                            temp[item] = get_component_names_per_ticket(len(issue['fields'][item]),
                                                                        issue['fields'][item],
                                                                        component_names_standard)
                    else:
                        try:
                            temp[item] = issue['fields'][item]['name']
                        except KeyError:
                            temp[item] = ''
                else:
                    temp[item] = ''

            if len(temp) == 1 or temp['components'] == '':  # no contents Or value of components is empty
                continue

            results.append(temp)
    elif project.component_field == Project.INDICATOR:  # use CEEQ Indicator

        indicator_field = project.instance.indicator_field

        for issue in project.fetch_jira_data['issues']:
            temp = {}
            temp['key'] = issue['key']
            for item in issue['fields']:
                if indicator_field not in issue['fields'] or not issue['fields'][indicator_field]:  # no ceeq_indicator field or ceeq_indicator == None
                    continue

                # Closed and Resolution Blacklist not counted
                if issue['fields']['resolution'] \
                        and issue['fields']['resolution']['name'] in project.resolution_blacklist\
                        and issue['fields']['status']['name'] == 'Closed':
                    continue

                # collect data
                if issue['fields'][item]:
                    if item == 'created':
                        temp[item] = issue['fields'][item]
                    elif item == 'versions':
                        temp[item] = issue['fields'][item][0]['name']
                    elif item in ['customfield_13286', 'customfield_10092']:
                        temp[item] = issue['fields'][item]['value']
                    elif item == indicator_field:
                        try:
                            temp['components'] = issue['fields'][item]['value'] + '/' + issue['fields'][item]['child']['value']
                        except KeyError:
                            temp['components'] = ''
                    elif item != 'components':
                        temp[item] = issue['fields'][item]['name']
                else:
                    if item != 'components':  # field 'Components==[]'
                        temp[item] = ''

            if len(temp) == 1:
                continue

            results.append(temp)

    return results


def get_component_names_per_ticket(component_len, components, component_names_standard):

    # if first item-component is not in framework, then check next, until end
    for i in range(component_len):
        try:
            component = (components[i]['name'])
        except UnicodeEncodeError:
            component = ''.join(components[i]['name']).encode('utf-8').strip()
            component = component.decode('utf-8')
        if component.startswith(tuple(component_names_standard)):
            return component
        else:
            continue

    return None


def get_projects_score_from_set(projects, data, charts_max, projects_count):
    for project in projects:
        score = project.internal_score
        if score == 103:
            continue
        else:
            projects_count += 1
            if projects_count == charts_max:
                break
            if score < 10:
                data['score'].append(str(score))
            else:
                data['score'].append(str(0))

        if project.query_field == project.QUERY_VERSION:
            data['categories'].append(project.jira_key.upper() + '-' + project.jira_version)
        else:
            data['categories'].append(project.name.upper())

        data['id'].append(str(project.id))

