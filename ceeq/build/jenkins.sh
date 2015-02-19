#!/bin/sh

virtualenv --no-site-packages --clear env
source /usr/local/virtualenvs/ceeq/bin/activate

pip install --download-cache /tmp/jenkins/pip-cache -r requirements/jenkins.txt

python manage.py test --jenkins --settings=ceeq.settings.dev