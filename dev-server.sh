#!/bin/bash
# Helper script to run local dev server using the venv

# Get directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PYTHON="$DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment python not found at $VENV_PYTHON"
    echo "Please create venv: python3 -m venv .venv"
    exit 1
fi

echo "Starting Deletarr API server..."
export DELETARR_ENV=local
# Check for DELETARR_CONFIG, otherwise standard config
if [ -z "$DELETARR_CONFIG" ]; then
    export DELETARR_CONFIG="$DIR/config/config.yml"
    echo "Using default config: $DELETARR_CONFIG"
fi

# Run uvicorn via python -m to ensure we use the venv packages
"$VENV_PYTHON" -m uvicorn deletarr.api:app --reload --host 0.0.0.0 --port 8000
