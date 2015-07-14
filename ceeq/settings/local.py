from base import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

if socket.gethostname() == 'sliu-OptiPlex-GX520':  # desktop
    #STATIC_URL = 'http://apps.qaci01.wic.west.com/static/'
    STATICFILES_DIRS = ('/opt/static/',)
elif socket.gethostname() == 'OM1960L1':
    STATIC_ROOT = '/static/'
    STATICFILES_DIRS = ('c:/static/',)
    JIRA_API_URL_TOTAL_JIRAS = 'http://jira.west.com/rest/api/2/search?fields=%s&maxResults=100&jql=project=' % (JIRA_API_FIELDS)

# INSTALLED_APPS += ('debug_toolbar',)
# MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
# INTERNAL_IPS = ('127.0.0.1', '10.6.20.127')


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'ceeq',
#         'USER': 'visilog',
#         'PASSWORD': '6ewuON0>;wHTe(DttOwjg#5NY)U497xKVwOxmQt60A1%}r:@qC&`7OdSP8u[.l[',
#         'HOST': 'linux6437.wic.west.com',
#         'PORT': '5432'
#     }
# }