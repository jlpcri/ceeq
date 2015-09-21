from ceeq.apps.calculator.models import ImpactMap
from ceeq.apps.queries.models import Instance


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


def parse_jira_data(data, component_names_standard):
    results = []
    for issue in data:
        temp = {}
        temp['key'] = issue['key']
        for item in issue['fields']:
            if issue['fields'][item]:
                if item == 'created':
                    temp[item] = issue['fields'][item]
                elif item in ['customfield_13286', 'customfield_10092']:
                    temp[item] = issue['fields'][item]['value']
                elif item == 'versions':
                    temp[item] = issue['fields'][item][0]['name']
                elif item == 'components':
                    components = issue['fields'][item]
                    component_len = len(components)
                    if component_len == 1:
                        temp[item] = components[0]['name']
                    else:
                        name = get_component_names_per_ticket(component_len, components, component_names_standard)
                        if name:
                            temp[item] = name
                else:
                    temp[item] = issue['fields'][item]['name']
            else:
                temp[item] = ''

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
