#! /bin/bash

source /home/sliu/.virtualenvs/ceeq/bin/activate
python /home/sliu/Projects/ceeq/manage.py daily_score_log --settings=ceeq.settings.local
deactivate
