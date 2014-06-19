from django.contrib.auth.models import User
from django.db import models


class UserSettings(models.Model):
    user = models.OneToOneField(User)

    bug = models.BooleanField(default=True)
    new_feature = models.BooleanField(default=False)
    task = models.BooleanField(default=False)
    improvement = models.BooleanField(default=False)
