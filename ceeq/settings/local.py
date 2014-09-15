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