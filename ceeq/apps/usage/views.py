from datetime import datetime

from ceeq.apps.queries.models import Project
from models import ProjectAccess


def update_project_access_history(request):
    projects = Project.objects.filter(complete=False)
    total_access = 0
    today = datetime.today().date()

    for project in projects:
        score_history = project.scorehistory_set.all()
        for item in score_history:
            if item.access and item.created.today().date() == today:
                total_access += 1

    try:
        project_access = ProjectAccess.objects.latest('created')
        if project_access.created.today().date() == today:
            project_access.total = total_access
            project_access.save()
        else:
            project_access = ProjectAccess.objects.create(total=total_access)
    except ProjectAccess.DoesNotExist:
        project_access = ProjectAccess.objects.create(total=total_access)
