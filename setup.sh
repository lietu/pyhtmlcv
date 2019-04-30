#!/usr/bin/env sh
set -exu

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
VIRTUALENV="$SCRIPTPATH/.venv"

if [ ! -d "$VIRTUALENV" ]; then
    pip install virtualenv
    virtualenv .venv
fi

source ".venv/bin/activate"
pip install requirements.txt
