from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from ceeq.apps.calculator.tasks import calculate_score
from ceeq.apps.queries.models import Project


def calculate_score_all(request):
    projects = Project.objects.filter(complete=False)
    for project in projects:
        calculate_score(project.id)

    return HttpResponseRedirect(reverse('q_projects'))


