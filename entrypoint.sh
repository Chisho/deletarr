#!/bin/sh

# Ensure config directory exists (it should be mounted)
if [ ! -d "/config" ]; then
    echo "Warning: /config directory not found. Using default config location or internal defaults."
fi

echo "Starting Deletarr Web UI + Scheduler..."
exec uvicorn deletarr.api:app --host 0.0.0.0 --port 8000
