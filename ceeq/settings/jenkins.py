from base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST_NAME': 'test_database.db'
    }
}

INSTALLED_APPS += ('discover_jenkins',)

TEST_RUNNER = 'discover_jenkins.runner.DiscoverCIRunner'

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

