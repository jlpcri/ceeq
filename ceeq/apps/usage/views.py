from datetime import datetime
import json
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

from ceeq.apps.queries.models import Project
from models import ProjectAccess


def update_project_access_history(request):
    """
    Update Project Access count per day
    :param request:
    :return:
    """
    projects = Project.objects.filter(complete=False)
    total_access = 0
    today = datetime.today().date()

    for project in projects:
        score_history = project.scorehistory_set.all()
        for item in score_history:
            if item.access and item.created.date() == today:
                total_access += 1

    project_accesses = ProjectAccess.objects.all()
    for project_access in project_accesses:
        if project_access.created.date() == today:
            project_access.total = total_access
            project_access.save()
            break
    else:
        project_access = ProjectAccess.objects.create(total=total_access)


def usage(request):
    if request.method == 'GET':
        return render(request, 'usage.html')

    return HttpResponseNotFound()


def get_project_access_trend(request):
    project_accesses = ProjectAccess.objects.all().order_by('created')
    data = {}
    categories = []
    count = []

    for item in project_accesses:
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

        count.append(item.total)

    data['categories'] = categories
    data['count'] = count

    return HttpResponse(json.dumps(data), content_type='application/json')
