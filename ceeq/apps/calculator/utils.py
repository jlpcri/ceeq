from collections import OrderedDict
from django.conf import settings

__author__ = 'sliu'


def get_table_data(query_results, uat_type):
    print 'table: ', uat_type
    print query_results


def get_score_data(query_results, component_names_standard, uat_type):
    for item in query_results:
        print item
    component_names = []
    component_names_without_slash = []

    for item in query_results:
        component_names.append(item['components'])
        component_names_without_slash.append(truncate_after_slash(item['components']))

    component_names = list(OrderedDict.fromkeys(component_names))
    component_names_without_slash = list(OrderedDict.fromkeys(component_names_without_slash))

    print component_names
    print component_names_without_slash


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

