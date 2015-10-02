import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from ceeq.apps.calculator.utils import fetch_subcomponents_pie
from ceeq.apps.queries.models import Project


def project_sub_piechart(request, project_id):
    uat_type = request.GET.get('uat_type')
    component_type = request.GET.get('component_type')

    project = get_object_or_404(Project, pk=project_id)
    context = RequestContext(request, {
        'project': project,
        'uat_type': uat_type,
        'component_type': component_type,
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
        'uat_type_custom': request.GET.get('uat_type_custom', '')
    })

    return render(request, 'q_sub_component/project_sub_component.html', context)


def fetch_subcomponents_pie_component(request, project_id):
    uat_type = request.GET.get('uat_type', '')
    component_type = request.GET.get('component_type', '')

    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    uat_type_custom = request.GET.get('uat_type_custom', '')

    component_name = [component_type]
    sub_pie_data = fetch_subcomponents_pie(project_id,
                                           component_name,
                                           uat_type,
                                           start,
                                           end,
                                           uat_type_custom)

    return HttpResponse(json.dumps(sub_pie_data), content_type='application/json')



