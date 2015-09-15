from django.db import models
from django.contrib.postgres.fields import HStoreField, ArrayField


class ImpactMap(models.Model):
    """
    Human friendly name for a set of component impacts: Apps, Inbound, Outbound
    """
    name = models.TextField(unique=True)

    def __unicode__(self):
        return self.name


from ceeq.apps.queries.models import Project


class ComponentImpact(models.Model):
    """
    Component name used in CEEQ framework for different types of Projects
    """
    impact_map = models.ForeignKey(ImpactMap)
    component_name = models.TextField()
    impact = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = (('impact_map', 'component_name'), )
        ordering = ['impact_map', 'component_name']

    def __unicode__(self):
        return '{0}: {1}'.format(self.impact_map.name, self.component_name)


class SeverityMap(models.Model):
    """
    Weight of different severity of JIRA tickets
    """
    name = models.TextField(unique=True)
    blocker = models.IntegerField(default=0)
    critical = models.IntegerField(default=0)
    major = models.IntegerField(default=0)
    minor = models.IntegerField(default=0)
    trivial = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class ComponentComplexity(models.Model):
    """
    Used for Component Complexity calculation
    """
    project = models.ForeignKey(Project)
    component_name = models.TextField()
    complexity = models.IntegerField(default=0)

    class Meta:
        unique_together = (("project", "component_name"), )
        ordering = ['project', 'component_name']

    def __unicode__(self):
        return '{0}: {1}'.format(self.project.name, self.component_name)


class ResultHistory(models.Model):
    """
    Store results fetched from JIRA through Celery
    """
    project = models.ForeignKey(Project)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    confirmed = models.DateTimeField(auto_now=True, db_index=True)

    # query results from JIRA through celery
    query_results = ArrayField(HStoreField(), null=True)

    # if ceeq score is calculated or not
    scored = models.BooleanField(default=False)

    # Data table under pie chart
    internal_testing_table = ArrayField(ArrayField(models.CharField(max_length=20, null=True)))
    uat_testing_table = ArrayField(ArrayField(models.CharField(max_length=20, null=True)))
    combined_testing_table = ArrayField(ArrayField(models.CharField(max_length=20, null=True)))

    # component weighted factor
    score_by_component = ArrayField(ArrayField(models.CharField(max_length=20, null=True)), null=True)

    # ceeq score
    internal_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    uat_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overall_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __unicode__(self):
        return '{0}: {1}'.format(self.project.name, self.created)


class LiveSettings(models.Model):
    score_scalar = models.IntegerField(default=0)
    current_delay = models.IntegerField(default=0)  # minutes of dealy between CEEQ and live data



