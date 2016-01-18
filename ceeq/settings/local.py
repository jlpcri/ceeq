from base import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

# INSTALLED_APPS += (
#     'ceeq.apps.projects',
#     'ceeq.apps.defects_density'
# )

# LOGIN_URL = '/ceep/'

if socket.gethostname() == 'sliu-OptiPlex-GX520':  # desktop
    STATIC_URL = 'http://apps.qaci01.wic.west.com/static/'
    # STATICFILES_DIRS = ('/opt/static/',)
elif socket.gethostname() == 'OM1960L1':
    STATIC_ROOT = '/static/'
    STATICFILES_DIRS = ('c:/static/',)
    JIRA_API_URL_TOTAL_JIRAS = 'http://jira.west.com/rest/api/2/search?fields=%s&maxResults=100&jql=project=' % (JIRA_API_FIELDS)
elif socket.gethostname() == 'QAIMint':  # Alex's desktop
    STATIC_URL = 'http://apps.qaci01.wic.west.com/static/'
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES
    INTERNAL_IPS = ['127.0.0.1', '10.6.20.90', '10.6.20.91', '::1']

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

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'ceeq',
#         'USER': 'ceeq',
#         'PASSWORD': 'FkhfDhPx%A=-?h_snCMuQ$&%5crcx%tpxw24pVVp+U-UrXs4q6=uK=8^-evN-RxA',
#         'HOST': 'linux6437.wic.west.com',
#         'PORT': '5433'   # posgtres 9.4 instance
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ceeq',
        'USER': 'scorecard',
        'PASSWORD': 'scorecard_development',
        'HOST': 'qaci01.wic.west.com',
        'PORT': '5432',
        # 'PORT': '5433'  # another postgres instance
    }
}

