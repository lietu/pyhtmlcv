#!/usr/bin/env sh
set -exu

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
VIRTUALENV="$SCRIPTPATH/.venv"

if [ ! -d "$VIRTUALENV" ]; then
    pip install virtualenv
    virtualenv .venv
fi

. ".venv/bin/activate"

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

pip install -r requirements.txt
