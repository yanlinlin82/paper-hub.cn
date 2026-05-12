#!/bin/bash

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Usage: $0 [-h|--help] [-u|--upgrade]"
    echo "Setup or upgrade the environment"
    echo "Options:"
    echo "  --help         Show this help message and exit"
    echo "  -u, --upgrade  Upgrade the environment"
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$BACKEND_DIR/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"

#==========================================================#

cd "$BACKEND_DIR"

if [ "$1" == "-u" -o "$1" == "--upgrade" ]; then
    echo "Upgrading Python dependencies"
    uv lock --upgrade
    uv sync --no-install-project
else
    echo "Syncing Python dependencies"
    uv sync --no-install-project
fi

#==========================================================#

cd "$FRONTEND_DIR"

if [ "$1" == "-u" -o "$1" == "--upgrade" ]; then
    echo "Upgrading npm packages"
    npx npm-check-updates -u
fi
npm install

#==========================================================#
cd "$BACKEND_DIR"
echo "Setup done"
