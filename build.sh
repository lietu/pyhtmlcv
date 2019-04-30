#!/usr/bin/env sh
set -exu

if [ "${VIRTUAL_ENV:-}" -eq "" ]; then
    SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
    VIRTUALENV="$SCRIPTPATH/.venv"
    if [ -d "$VIRTUALENV" ]; then
        . ".venv/bin/activate"
    fi
fi

PYTHON=$(which python)
if [ -z "${PYTHON}" ]; then
    PYTHON=$(which python27)
    if [ -z "${PYTHON}" ]; then
        PYTHON=$(which python26)
    fi
fi

exec $PYTHON pyhtmlcv.py "$@"
