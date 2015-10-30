from base import *

DEBUG = False

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'TEST_NAME': 'test_database.db'
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_database',
        'USER': 'scorecard',
        'PASSWORD': 'scorecard_development',
        'HOST': 'qaci01.wic.west.com',
        # 'PORT': '5432',
        'PORT': '5433'  # another postgres instance
    }
}

INSTALLED_APPS += ('discover_jenkins',)

# TEST_RUNNER = 'discover_jenkins.runner.DiscoverCIRunner'

TEST_PROJECT_APPS = (
    'ceeq.apps.core',
    'ceeq.apps.calculator',
    'ceeq.apps.help',
    'ceeq.apps.queries',
    'ceeq.apps.search',
    'ceeq.apps.users'
)

TEST_TASKS = (
    'discover_jenkins.tasks.with_coverage.CoverageTask',
    'discover_jenkins.tasks.run_pylint.PyLintTask',
)

TEST_COVERAGE_EXCLUDES_FOLDERS = [
    '/usr/local/*',
    'ceeq/apps/*/tests/*',
]

