#!/usr/bin/env sh
set -exu

if [ "${VIRTUAL_ENV:-}" -eq "" ]; then
    SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
    VIRTUALENV="$SCRIPTPATH/.venv"

    if [ ! -d "$VIRTUALENV" ]; then
        pip install virtualenv
        virtualenv .venv
    fi

    . ".venv/bin/activate"
fi

pip install -r requirements.txt
