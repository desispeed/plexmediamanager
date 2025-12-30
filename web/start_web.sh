#!/bin/bash
# Start Plex Media Manager Web Server

# Load environment variables if .env file exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set default values
export PLEX_URL="${PLEX_URL:-http://mirror.seedhost.eu:32108}"
export PLEX_TOKEN="${PLEX_TOKEN:-j89Uh7HxZfGPEj3nkq9Z}"
export TOTAL_CAPACITY_GB="${TOTAL_CAPACITY_GB:-3700}"
export SSH_HOST="${SSH_HOST:-mirror.seedhost.eu}"
export SSH_USER="${SSH_USER:-desispeed}"
export REMOTE_PATH="${REMOTE_PATH:-/home32}"
export PORT="${PORT:-5000}"
export FLASK_DEBUG="${FLASK_DEBUG:-False}"
export FLASK_ENV="${FLASK_ENV:-production}"

echo "🚀 Starting Plex Media Manager Web Server..."
echo "📡 Plex Server: $PLEX_URL"
echo "🌐 Port: $PORT"
echo "🔧 Environment: $FLASK_ENV"
echo ""

# Start the Flask app
python3 app.py
