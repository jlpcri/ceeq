from django.shortcuts import render

from ceeq.apps.calculator.models import LiveSettings


def guide(request):
    context = {
        'superuser': request.user.is_superuser
    }

    return render(request, 'help/guide.html', context)


def guide_framework(request):
    try:
        ls = LiveSettings.objects.get(pk=2)
    except LiveSettings.DoesNotExist:
        ls = {
            'issue_status_open': ['Open', 'In Progress', 'Reopened', 'Discovery', 'Review', 'Pending', 'Research', 'Pending Estimate'],
            'issue_status_resolved': ['Resolved', 'UAT Testing', 'Done'],
            'issue_status_closed':  ['Closed', 'Complete']
        }
    context = {
        'base_url': 'http://' + request.get_host(),
        'ls': ls
    }

    return render(request, 'help/guide_framework.html', context)


def faq(request):
    return render(request, 'help/faq.html')