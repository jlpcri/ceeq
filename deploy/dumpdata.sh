#!/bin/bash

source /usr/local/bin/virtualenvwrapper.sh

workon ceeq_new

./manage.py dumpdata queries > dumpdata/queries.json --settings=ceeq.settings.local
./manage.py dumpdata calculator.ImpactMap calculator.ComponentImpact calculator.SeverityMap calculator.ComponentComplexity calculator.LiveSettings > dumpdata/calculator.json --settings=ceeq.settings.local
./manage.py dumpdata usage > dumpdata/usage.json --settings=ceeq.settings.local
deactivate