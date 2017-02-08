from django.db import models
from django.contrib.postgres.fields import ArrayField

from jira import JIRA, JIRAError
from requests import ConnectionError

from ceeq.apps.calculator.models import ImpactMap
from ceeq.apps.users.models import UserSettings


class Instance(models.Model):
    url = models.URLField()
    jira_user = models.TextField()
    password = models.TextField()
    jira_fields = ArrayField(models.CharField(max_length=50, default=''), null=True)
    indicator_field = models.TextField(null=True, blank=True)  # The custom field ID for the CEEQ indicator

    def __unicode__(self):
        return self.url


class Project(models.Model):
    # Component Field Options
    COMPONENT = 1
    INDICATOR = 2
    PARSE_JIRA_CHOICES = (
        (COMPONENT, 'CEEQ Components'),
        (INDICATOR, 'CEEQ Indicator')
    )

    # Query JIRA data Options
    QUERY_JQL = 'JQL Query'
    QUERY_VERSION = 'Project Version'
    QUERY_JIRA_CHOICES = (
        (QUERY_JQL, 'JQL Query'),
        (QUERY_VERSION, 'Project Version')
    )

    # No jira data var
    NO_JIRA_DATA = 'No JIRA Data'

    name = models.TextField(unique=True)  # Human-friendly name
    # Add relation of Project and User
    members = models.ManyToManyField(UserSettings, blank=True)

    jira_key = models.CharField(max_length=16)
    jira_version = models.TextField(default='All Versions')
    instance = models.ForeignKey(Instance)
    issue_types = ArrayField(models.CharField(max_length=50, blank=True), default=['Bug', 'Bug task', 'Bug (QA)', 'Bug (UAT)'])
    resolution_blacklist = ArrayField(models.CharField(max_length=50, blank=True),
                                      default=['Duplicate', 'Works as Designed', 'Working as Required'])
    # component_field = models.IntegerField(default=1)  # Choice between compoent and Indicator
    component_field = models.IntegerField(choices=PARSE_JIRA_CHOICES, default=COMPONENT)
    impact_map = models.ForeignKey(ImpactMap)
    active = models.BooleanField(default=True)  # tracking JIRA projects or not
    complete = models.BooleanField(default=False)  # CEEQ projects complete or not

    # add use jql to access isr
    query_field = models.CharField(max_length=20, choices=QUERY_JIRA_CHOICES,
                                   default=QUERY_VERSION)
    query_jql = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return '{0}: {1}: {2}'.format(self.name, self.jira_key, self.jira_version)
    
    @property
    def fetch_jira_data(self):
        jira = self.open_jira_connection()

        if self.query_field == self.QUERY_VERSION:
            try:
                if self.jira_version == 'All Versions':
                    data = jira.search_issues('project={0}'.format(self.jira_key))
                else:
                    data = jira.search_issues('project={0}&affectedversion=\'{1}\''.format(self.jira_key, self.jira_version),)
            except JIRAError:
                return self.NO_JIRA_DATA

            total = data.total
            # jira.west.com limited to fetch 1000 tickets per time
            if total > 1000:
                data = {'issues': []}
                for i in range(total / 1000 + 1):
                    if self.jira_version == 'All Versions':
                        temp = jira.search_issues('project={0}'.format(self.jira_key),
                                                  startAt=1000 * i,
                                                  maxResults=1000,
                                                  fields=self.instance.jira_fields,
                                                  json_result=True)
                        for item in temp['issues']:
                            data['issues'].append(item)
                    else:
                        temp = jira.search_issues('project={0}&affectedversion=\'{1}\''.format(self.jira_key, self.jira_version),
                                                  startAt=1000 * i,
                                                  maxResults=1000,
                                                  fields=self.instance.jira_fields,
                                                  json_result=True)
                        for item in temp['issues']:
                            data['issues'].append(item)
            else:
                if self.jira_version == 'All Versions':
                    data = jira.search_issues('project={0}'.format(self.jira_key),
                                              maxResults=total,
                                              fields=self.instance.jira_fields,
                                              json_result=True)
                else:
                    data = jira.search_issues('project={0}&affectedversion=\'{1}\''.format(self.jira_key, self.jira_version),
                                              maxResults=total,
                                              fields=self.instance.jira_fields,
                                              json_result=True)
        else:
            try:
                tmp = jira.search_issues(self.query_jql)
                data = jira.search_issues(self.query_jql,
                                          maxResults=tmp.total,
                                          fields=self.instance.jira_fields,
                                          json_result=True)
                # print data
            except JIRAError:
                return self.NO_JIRA_DATA

        return data

    @property
    def fetch_jira_versions(self):
        versions = []

        if self.query_field == self.QUERY_VERSION:
            jira = self.open_jira_connection()
            v = jira.project_versions(self.jira_key.upper())
            for item in v:
                versions.append(item.name)

        versions.append('All Versions')

        return versions
    
    def open_jira_connection(self):
        try:
            conn = JIRA(
                options={'server': self.instance.url, 'verify': False},
                basic_auth=(self.instance.jira_user, self.instance.password)
                )
        except ConnectionError:
            conn = JIRA(
                options={'server': self.instance.url, 'verify': False},
                basic_auth=(self.instance.jira_user, self.instance.password))
            conn._session.proxies = {
                'http': 'qaci01.wic.west.com:3128',
                'https': 'qaci01.wic.west.com:3128'
            }
        return conn

    @property
    def internal_score(self):
        try:
            score = self.scorehistory_set.latest('created').internal_score[0]
            return score
        except (ScoreHistory.DoesNotExist, TypeError):
            return 0

    @property
    def uat_score(self):
        try:
            score = self.scorehistory_set.latest('created').uat_score[0]
            return score
        except (ScoreHistory.DoesNotExist, TypeError):
            return 0

    @property
    def overall_score(self):
        try:
            score = self.scorehistory_set.latest('created').combined_score[0]
            return score
        except (ScoreHistory.DoesNotExist, TypeError):
            return 0

    @property
    def jira_data_latest_update(self):
        return self.resulthistory_set.latest('confirmed').confirmed

    @property
    def member_usernames(self):
        return [str(u.user.username) for u in self.members.all()]


class ScoreHistory(models.Model):
    """
    Store Combined/Internal/UAT daily score
    """
    project = models.ForeignKey(Project)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    access = models.BooleanField(default=False)

    # Save daily CEEQ Score
    combined_score = ArrayField(models.DecimalField(max_digits=10, decimal_places=2, default=0), null=True)
    internal_score = ArrayField(models.DecimalField(max_digits=10, decimal_places=2, default=0), null=True)
    uat_score = ArrayField(models.DecimalField(max_digits=10, decimal_places=2, default=0), null=True)

    def __unicode__(self):
        return '{0}: {1}: {2}: {3}'.format(self.project.name,
                                           self.created,
                                           self.internal_score,
                                           self.access)

