#!/usr/bin/env bash

# Find the python interpreter

PYTHON=$(which python)
if [ -z "${PYTHON}" ]; then
	PYTHON=$(which python27)
	if [ -z "${PYTHON}" ]; then
		PYTHON=$(which python26)
	fi
fi

# Run the tool
"${PYTHON}" pyhtmlcv.py $@

