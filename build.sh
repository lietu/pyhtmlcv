#!/usr/bin/env sh
set -exu

if [ -d "$VIRTUALENV" ]; then
    . ".venv/bin/activate"
fi

PYTHON=$(which python)
if [ -z "${PYTHON}" ]; then
	PYTHON=$(which python27)
	if [ -z "${PYTHON}" ]; then
		PYTHON=$(which python26)
	fi
fi

exec $PYTHON pyhtmlcv.py "$@"
