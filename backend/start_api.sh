#!/bin/bash
# Start Plex Manager API

cd "$(dirname "$0")"

# Load configuration from plex-cleanup config
if [ -f "../../plex-cleanup/config.sh" ]; then
    source ../../plex-cleanup/config.sh
    export PLEX_URL
    export PLEX_TOKEN
    export MAX_VIEWS
    export DAYS_NOT_WATCHED
fi

echo "Starting Plex Manager API..."
python3 api.py
