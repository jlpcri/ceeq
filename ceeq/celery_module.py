import os
import socket

from celery import Celery

from django.conf import settings


if socket.gethostname() in ("sliu-OptiPlex-GX520", "QAIMint"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ceeq.settings.local")
elif socket.gethostname() == "qaci01":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ceeq.settings.dev")
elif socket.gethostname() == "linux6436":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ceeq.settings.qa")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ceeq.settings.base")

app = Celery('ceeq')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name='tasks')

