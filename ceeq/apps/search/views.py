from django.shortcuts import render
from django.template import RequestContext

from ceeq.apps.projects.models import Project


def search(request):
    if request.GET:
        query = request.GET.get('query', '')

        projects = Project.objects.filter(name__icontains=query)
        context = RequestContext(request, {
            'projects': projects
        })
        return render(request, 'search.html', context)
