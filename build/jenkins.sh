#!/bin/sh

virtualenv --no-site-packages --clear env
. /usr/local/virtualenvs/ceeq_new/bin/activate

pip install --download-cache /tmp/jenkins/pip-cache -r requirements/jenkins.txt

python manage.py jenkins --enable-coverage --settings=ceeq.settings.jenkins