from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from ceeq.apps.projects.models import ProjectComponentsDefectsDensity


def dd_all(request):
    dds = ProjectComponentsDefectsDensity.objects.all()
    context = RequestContext(request, {
        'dds': dds,
        'superuser': request.user.is_superuser
    })
    return render(request, 'dd_list.html', context)


def dd_detail(request, dd_id):
    pass


def dd_edit(request, dd_id):
    pass


def dd_new(request):
    pass


def dd_delete(request, dd_id):
    dd = get_object_or_404(ProjectComponentsDefectsDensity, pk=dd_id)
    dd.delete()
    messages.success(request, "DD record \"{0}\" has been deleted.".format(dd.id))

    return redirect(reverse('ceeq.apps.defects_density.views.dd_all'))