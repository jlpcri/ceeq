#!/bin/bash

source /usr/local/bin/virtualenvwrapper.sh

workon ceeq_new

./manage.py dumpdata auth > dumpdata/auth.json --settings=ceeq.settings.local
./manage.py dumpdata users > dumpdata/users.json --settings=ceeq.settings.local
./manage.py dumpdata queries > dumpdata/queries.json --settings=ceeq.settings.local
./manage.py dumpdata calculator --exclude=calculator.ResultHistory  > dumpdata/calculator.json --settings=ceeq.settings.local
./manage.py dumpdata usage > dumpdata/usage.json --settings=ceeq.settings.local
deactivate