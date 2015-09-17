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


def parse_jira_data(data):
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
                elif item in ['components', 'versions']:
                    temp[item] = issue['fields'][item][0]['name']
                else:
                    temp[item] = issue['fields'][item]['name']
            else:
                temp[item] = ''

        results.append(temp)

    return results
