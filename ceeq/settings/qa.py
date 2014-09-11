from base import *

#Use QACI01 as proxy server for staging server
JIRA_PROXY = {
    'http': 'http://qaci01.wic.west.com:3128',
}

DEBUG = False

#SETTINGS_MODULE = 'ceeq.settings.qa'

ALLOWED_HOSTS = [
    'apps.qaci01.wic.west.com',
    'apps.qaci01',
    'linux6438.wic.west.com',
    'linux6438'
]