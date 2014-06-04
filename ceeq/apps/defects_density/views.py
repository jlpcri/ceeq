from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from ceeq.apps.projects.models import ProjectComponentsDefectsDensity
from ceeq.apps.users.views import user_is_superuser


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


@user_passes_test(user_is_superuser)
def dd_delete(request, dd_id):
    dd = get_object_or_404(ProjectComponentsDefectsDensity, pk=dd_id)
    dd.delete()
    messages.success(request, "Defects Density project: \"{0}\", version: \"{1}\", data: \"{2}\" has been deleted.".format(dd.project.name, dd.version, dd.created))

    return redirect(reverse('ceeq.apps.users.views.home'))