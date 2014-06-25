from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.core.urlresolvers import reverse


class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)
    jira_name = models.CharField(max_length=200)  # name of the related project in JIRA
    score = models.DecimalField(max_digits=5, decimal_places=2, default=-9)
    created = models.DateTimeField('date added', auto_now_add=True)
    modified = models.DateTimeField('date modified', auto_now=True)

     #Domain Testing Characteristics 0-5
    accuracy = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    suitability = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    interoperability = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    functional_security = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    usability = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    accessibility = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])

    #Technical Testing Characteristics 0-5
    technical_security = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    reliability = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    efficiency = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    maintainability = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    portability = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])

    def __unicode__(self):
        return unicode(self.name)


class ProjectComponentsDefectsDensity(models.Model):
    project = models.ForeignKey(Project)
    version = models.CharField(max_length=200)
    created = models.DateField()
    # log ceeq score per day per version
    ceeq = models.DecimalField(max_digits=5, decimal_places=3, default=0)


    cxp = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    platform = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    reports = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    application = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    voiceSlots = models.DecimalField(max_digits=5, decimal_places=3, default=0)

    class Meta:
        #unique_together = (("project", "created", "version"),)
        ordering = ['created', 'version']


class FrameworkParameter(models.Model):
    #Store framework parameters: jira_issue_weight_sum, vaf_ratio, vaf_exp
    parameter = models.CharField(max_length=200, unique=True)
    value = models.DecimalField(max_digits=3, decimal_places=2, default=0)







