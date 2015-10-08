from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from ceeq.apps.calculator.tasks import calculate_score
from ceeq.apps.queries.models import Project
from ceeq.apps.users.views import user_is_superuser


@user_passes_test(user_is_superuser)
def calculate_score_all(request):
    projects = Project.objects.filter(complete=False)
    for project in projects:
        calculate_score.delay(project.id)

    # calculate_score(8)
    return HttpResponseRedirect(reverse('queries:projects'))


