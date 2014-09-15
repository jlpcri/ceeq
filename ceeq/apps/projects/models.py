from multiprocessing import Process, Queue
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.conf import settings
import requests


class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)
    jira_name = models.CharField(max_length=200)  # name of the related project in JIRA
    jira_version = models.CharField(max_length=200, default='All Versions')  # version of issues in JIRA
    score = models.DecimalField(max_digits=5, decimal_places=2, default=-9)
    created = models.DateTimeField('date added', auto_now_add=True)
    modified = models.DateTimeField('date modified', auto_now=True)
    active = models.BooleanField(default=True)  # tracking JIRA projects or not
    complete = models.BooleanField(default=False)  # CEEQ projects complete or not

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

    @property
    def fetch_jira_data(self):

        data = requests.get(settings.JIRA_API_URL_TOTAL_JIRAS + self.jira_name,
                            proxies=settings.JIRA_PROXY,
                            auth=('readonly_sliu_api_user', 'qualityengineering')).json()
        #print 'total: ', data['total']

        from jira.client import JIRA
        jira_data = JIRA(server='http://jira.west.com',
                         basic_auth=('readonly_sliu_api_user', 'qualityengineering'),
                         )


        if len(data) == 2:
            if data['errorMessages']:
                return 'No JIRA Data'
        else:
            results = {}
            jira_project = jira_data.project(self.jira_name.upper())

            jira_issues = jira_data.search_issues('project=%s' % self.jira_name,
                                                  fields=settings.JIRA_API_FIELDS,
                                                  maxResults=data['total'],
                                                  )
            components = [c.name for c in jira_project.components]
            versions = [v.name for v in jira_project.versions]

            results['components'] = components
            results['versions'] = versions
            results['issues'] = jira_issues

            return results


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


