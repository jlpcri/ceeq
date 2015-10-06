from celery.schedules import crontab

# Celery config
CELERY_ACCEPT_CONTENT = ['pickle', 'json', ]
CELERY_ENABLE_UTC = False
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_RESULT_PERSISTENT = True
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_TASK_RESULT_EXPIRES = None   # no result is return back

CELERYBEAT_SCHEDULE = {
    # Execute every 10 minutes every day
    'fetch-jira-data-run': {
        'task': 'ceeq.apps.queries.tasks.fetch_jira_data_run',
        'schedule': crontab(minute='*/5')
    },
    # Execute every 12 hours every day
    'daily-score-log': {
        'task': 'ceeq.apps.queries.tasks.daily_score_log',
        'schedule': crontab(minute=0, hour='*/12')
    }
}

CELERY_TIMEZONE = 'US/Central'