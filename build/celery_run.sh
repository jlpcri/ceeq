#!/bin/bash

# This script for running celery on local desktop
# required: 'sudo apt-get install rabbitmq-server'

source ~/.virtualenvs/ceeq_new/bin/activate

cd ~/Projects/ceeq_new

~/.virtualenvs/ceeq_new/bin/celery -A ceeq worker -l info