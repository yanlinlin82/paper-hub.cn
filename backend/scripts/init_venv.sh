#!/bin/bash

upgrade=false
dev=false
while getopts "ud" opt; do
	case $opt in
		u) upgrade=true ;;
		d) dev=true ;;
		*) echo "Usage: $0 [-u|--upgrade] [-d|--dev]" && exit 1 ;;
	esac
done

[ ! -d .venv ] && python3 -m venv .venv
. .venv/bin/activate

pip install -U pip pip-tools
if [ "$upgrade" == true ] || [ ! -f requirements_dev.txt ] || [ ! -f requirements.txt ]; then
	pip-compile -U requirements_dev.in -o requirements_dev.txt
	pip-compile -U requirements.in -o requirements.txt
fi

if [ "$dev" == true ]; then
	pip install -r requirements_dev.txt
else
	pip install -r requirements.txt
fi
