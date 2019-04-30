#!/usr/bin/env sh
set -exu

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
VIRTUALENV="$SCRIPTPATH/.venv"

if [ ! -d "$VIRTUALENV" ]; then
    pip install virtualenv
    virtualenv .venv
fi

. ".venv/bin/activate"

pip install --user -r requirements.txt
