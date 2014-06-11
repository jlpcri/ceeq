import json
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext

from ceeq.apps.projects.models import Project, ProjectComponentsDefectsDensity
from ceeq.apps.users.views import user_is_superuser
from forms import DefectDensityForm


def dd_all(request):
    projects = Project.objects.all()
    dds = ProjectComponentsDefectsDensity.objects.all()
    context = RequestContext(request, {
        'projects': projects,
        'dds': dds,
        'superuser': request.user.is_superuser
    })
    return render(request, 'projects_start.html', context)


def dd_detail(request, dd_id):
    dd = get_object_or_404(ProjectComponentsDefectsDensity, pk=dd_id)
    form = DefectDensityForm(instance=dd)

    context = RequestContext(request, {
        'form': form,
        'dd': dd,
    })
    return render(request, 'dd_detail.html', context)


def dd_edit(request, dd_id):
    dd = get_object_or_404(ProjectComponentsDefectsDensity, pk=dd_id)

    if request.method == "POST":
        form = DefectDensityForm(request.POST, instance=dd)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                dd_exist = ProjectComponentsDefectsDensity.objects.filter(project=form_data['project'],
                                                                          version=form_data['version'],
                                                                          created=form_data['created'])
                if dd_exist.count() > 1:
                    messages.warning(request, 'Record already exist')
                    return redirect(dd_all)
                else:
                    dd = form.save()
            except ProjectComponentsDefectsDensity.DoesNotExist:
                dd = form.save()
            messages.success(request, "Project Component Defect Density is saved.")
            return redirect(dd_all)
        else:
            messages.error(request, "Correct errors in the form.")
            context = RequestContext(request, {
                'form': form,
                'dd': dd,
            })
            return render(request, 'dd_detail.html', context)
    else:
        return redirect(dd_all)


def dd_new(request):
    pass


@user_passes_test(user_is_superuser)
def dd_delete(request, dd_id):
    dd = get_object_or_404(ProjectComponentsDefectsDensity, pk=dd_id)
    dd.delete()
    messages.success(request, "Defects Density project: \"{0}\", version: \"{1}\", data: \"{2}\" has been deleted.".format(dd.project.name, dd.version, dd.created))

    return redirect(reverse('ceeq.apps.users.views.home'))


def fetch_dds_json(request, project_id):
    if project_id == '1000000':
        dds = ProjectComponentsDefectsDensity.objects.all().order_by('project', 'version')
    else:
        dds = ProjectComponentsDefectsDensity.objects.filter(project=project_id)

    dds_json = []
    for dd in dds:
        temp = []
        temp.append(dd.project.name)
        temp.append(dd.version)
        temp.append(str(dd.created))
        temp.append(float(dd.cxp))
        temp.append(float(dd.outbound))
        temp.append(float(dd.platform))
        temp.append(float(dd.reports))
        temp.append(float(dd.applications))
        temp.append(float(dd.voiceSlots))
        dds_json.append(temp)

    return HttpResponse(json.dumps(dds_json), content_type="application/json")