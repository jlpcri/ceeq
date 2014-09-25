#!/bin/bash
VENV=/opt/ceeq/env
if [ -z $VENV ]; then
    echo "usage: runinenv [virtualenv_path] CMDS"
    exit 1
fi
. /opt/rh/python27/enable
source ${VENV}/bin/activate
#shift 1
echo "Executing $@ in ${VENV}"
exec "$@"
deactivate
