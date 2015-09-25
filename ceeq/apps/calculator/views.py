from django.shortcuts import redirect
from ceeq.apps.calculator.tasks import calculate_score
from ceeq.apps.queries.models import Project
from ceeq.apps.queries.views import projects as query_home


def calculate_score_all(request):
    projects = Project.objects.filter(complete=False)
    for project in projects:
        calculate_score(project.id)

    return redirect(query_home)


