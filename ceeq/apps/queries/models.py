from django.db import models
from django.contrib.postgres.fields import ArrayField

from ceeq.apps.calculator.models import ImpactMap


class Instance(models.Model):
    url = models.URLField()
    jira_user = models.TextField()
    password = models.TextField()
    indicator_field = models.TextField()  # The custom field ID for the CEEQ indicator

    def __unicode__(self):
        return self.url


class Project(models.Model):
    name = models.TextField(unique=True)  # Human-friendly name
    jira_key = models.CharField(max_length=16)
    jira_version = models.TextField()
    instance = models.ForeignKey(Instance)
    issue_types = ArrayField(models.CharField(max_length=50, blank=True), default='Bug')
    resolution_blacklist = ArrayField(models.CharField(max_length=50, blank=True))
    component_field = models.IntegerField()  # Choice between compoent and Indicator
    impact_map = models.ForeignKey(ImpactMap)

    def __unicode__(self):
        return '{0}: {1}: {2}'.format(self.name, self.jira_key, self.jira_version)
