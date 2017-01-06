from django.contrib.auth.models import User
from django.db import models


class UserSettings(models.Model):
    user = models.OneToOneField(User)

    bug = models.BooleanField(default=True)   # 1
    new_feature = models.BooleanField(default=False)  # 2
    task = models.BooleanField(default=False)  # 3
    improvement = models.BooleanField(default=False)  # 4
    suggested_improvement = models.BooleanField(default=False)  # 15
    environment = models.BooleanField(default=False)  # 17

    def __unicode__(self):
        if self.user.first_name:
            return "{0} {1}".format(self.user.first_name, self.user.last_name)
        else:
            return self.user.username

    class Meta:
        ordering = ['user__first_name']
