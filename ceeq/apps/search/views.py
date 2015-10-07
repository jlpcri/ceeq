from django.shortcuts import render
from django.template import RequestContext

from ceeq.apps.queries.models import Project


def search(request):
    if request.GET:
        query = request.GET.get('query', '')

        projects = Project.objects.filter(name__icontains=query)
        context = RequestContext(request, {
            'projects': projects,
            'superuser': request.user.is_superuser
        })
        return render(request, 'search/search.html', context)
