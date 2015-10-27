from celery.schedules import crontab
from kombu import Queue

# Celery config
CELERY_ACCEPT_CONTENT = ['pickle', 'json', ]
# CELERY_ENABLE_UTC = False
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_RESULT_PERSISTENT = True
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_TASK_RESULT_EXPIRES = None   # no result is return back

CELERY_ROUTES = {
    'ceeq.apps.queries.tasks.query_jira_data': {'queue': 'ceeq_queue'},
    'ceeq.apps.calculator.tasks.calculate_score': {'queue': 'ceeq_queue'},

}

CELERYBEAT_SCHEDULE = {
    # Execute every 5 minutes every day
    'fetch-jira-data-run': {
        'task': 'ceeq.apps.queries.tasks.fetch_jira_data_run',
        'schedule': crontab(minute='*/2'),
        'options': {'queue': 'ceeq_queue'}
    },
    # Execute in specified hour every day
    'daily-score-log': {
        'task': 'ceeq.apps.queries.tasks.daily_score_log',
        'schedule': crontab(minute=0, hour='0,8,10,12,14,16,18,20,23'),
        'options': {'queue': 'ceeq_queue'}
    }
}

CELERY_TIMEZONE = 'America/Chicago'
