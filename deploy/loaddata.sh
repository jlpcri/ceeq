#!/bin/bash

source /usr/local/bin/virtualenvwrapper.sh

workon ceeq_new

./manage.py loaddata dumpdata/auth.json --settings=ceeq.settings.local
./manage.py loaddata dumpdata/users.json --settings=ceeq.settings.local
./manage.py loaddata dumpdata/calculator.json --settings=ceeq.settings.local
./manage.py loaddata dumpdata/queries.json --settings=ceeq.settings.local
./manage.py loaddata dumpdata/usage.json --settings=ceeq.settings.local
deactivate