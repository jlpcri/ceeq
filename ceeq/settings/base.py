"""
Django settings for quality_of_solution project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

#Using LDAP
import socket
import ldap
from django_auth_ldap.config import LDAPSearch

LOGIN_URL = '/ceeq/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_ldap.backend.LDAPBackend',
)

AUTH_LDAP_SERVER_URI = "ldap://10.27.116.51"
AUTH_LDAP_BIND_DN = "cn=LDAP Query\\, Domino Server, OU=Service Accounts,DC=corp,DC=westworlds,DC=com"
AUTH_LDAP_BIND_PASSWORD = "Qu3ryLd@p"
AUTH_LDAP_USER_SEARCH = LDAPSearch('DC=corp,DC=westworlds,DC=com',
    ldap.SCOPE_SUBTREE, "(samaccountname=%(user)s)")

AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0
}

AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenname',
    'last_name': 'sn',
    'email': 'mail'
}


import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^)mf_^fz@e*e5zh%3=rtvnn@-2(u!3ezl%p8_y!q^qn)#8bqcr'

# SECURITY WARNING: don't run with debug turned on in production!


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tastypie',
    'ceeq.apps.core',
    'ceeq.apps.projects',
    'ceeq.apps.defects_density',
    'ceeq.apps.help',
    'ceeq.apps.users',
    'ceeq.apps.search',
    'ceeq.api',
    'south',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ceeq.urls'

WSGI_APPLICATION = 'ceeq.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'ceeq.db'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = ''

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

#JIRA_API_FIELDS = 'components,status,priority,versions,issuetype,resolution,created,resolutiondate'
#                                                                              workflow UAT   TFCC Is Root Cause
JIRA_API_FIELDS = 'components,status,priority,versions,issuetype,resolution,created,customfield_13286,customfield_10092'
# JIRA_API_MAX = 50
# JIRA_API_URL_TOTAL_JIRAS = 'http://jira.west.com/rest/api/2/search?fields=%s&maxResults=5&jql=project=' % (JIRA_API_FIELDS)
# JIRA_API_URL = 'http://jira.west.com/rest/api/2/search?fields=%s&maxResults=%d&startAt=%d&jql=project=%s'
# JIRA_API_URL_VERSIONS = 'http://jira.west.com/rest/api/2/project/%s/versions'
JIRA_API_USERNAME = 'readonly_sliu_api_user'
JIRA_API_PASSWORD = 'qualityengineering'

SESSION_COOKIE_NAME = 'ceeqSessionId'
# Age of session cookies, in seconds
SESSION_COOKIE_AGE = 43200  # 12 hours
# Save the session data on every request
SESSION_SAVE_EVERY_REQUEST = True

# ---------------------Pre Define Section --------------------

# Standard Component Name and its comparison ratio
from decimal import Decimal

# COMPONENT_NAMES_STANDARD = {
#     'Client': 0,
#     'CXP': 2,
#     'Platform': 4,
#     'Reports': 3,
#     'Application': 8,
#     'Voice': 3
# }

# Priority Weight of Issues in JIRA
ISSUE_PRIORITY_WEIGHT = {
    'blocker': Decimal(5) / 15,
    'critical': Decimal(4) / 15,
    'major': Decimal(3) / 15,
    'minor': Decimal(2) / 15,
    'trivial': Decimal(1) / 15
}

"""
 Issue Status
 1-open,
 3-In progress,
 4-reopen,
 5-resolved,
 6-closed,
 10001-UAT testing,
 10003-Discovery,
 10062-Review,
 10668-Pending,
 10669-Research
"""
ISSUE_STATUS_OPEN = ['1', '3', '4', '10003', '10062', '10668', '10669']
#issue_status_in_progress = '3'
ISSUE_STATUS_RESOLVED = ['5', '10001']
ISSUE_STATUS_CLOSED = ['6']
#issue_status_uat_testing = '10001'
#issue_status_discovery = '10003'

# 2-Won't Fix, 3-Duplicate, 6-Works as Design
ISSUE_RESOLUTION_NOT_COUNT = ['3', '6']

# 11 - External Limitation
ISSUE_RESOLUTION_EXTERNAL_LIMITATION = ['11']

# TFCC Is Root Cause - Test Data - 13499
ISSUE_TFCC_IS_ROOT_CAUSE = ['13499']

# data structure for broken issue status
ISSUE_STATUS_COUNT = {
    'open': 0,
    #'in_progress': 0,
    #'reopen': 0,
    'resolved': 0,
    'closed': 0,
    #'uat_testing': 0,
    #'discovery': 0
}

# issue status weight ratio
ISSUE_STATUS_WEIGHT = {
    'open': Decimal(7) / 10,
    #'in_progress': 0,
    #'reopen': 0,
    'resolved': Decimal(2) / 10,
    'closed': Decimal(1) / 10,
    #'uat_testing': 0,
    #'discovery': 0
}

# index of Open Resolved Closed issues per priority
ISSUE_STATUS_FIELDS = [
        ('blocker', [5, 6, 4]),
        ('critical', [8, 9, 7]),
        ('major', [11, 12, 10]),
        ('minor', [14, 15, 13]),
        ('trivial', [17, 18, 16])
    ]

#----------------EMAIL Backend----------------
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'ceeqwic@gmail.com'
EMAIL_HOST_PASSWORD = '^S=+c3gyYu6F74D'
EMAIL_PORT = 587