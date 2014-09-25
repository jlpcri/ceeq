#!/bin/bash

cd  /opt/ceeq

. /opt/rh/python27/enable
source env/bin/activate

nohup uwsgi --ini ceeq_uwsgi.ini

deactivate
