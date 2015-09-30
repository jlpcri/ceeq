from django.db import models
from django.contrib.postgres.fields import ArrayField


class ProjectAccess(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    total = models.IntegerField(default=0)

    def __unicode__(self):
        return '{0}: {1}'.format(self.created, self.total)
