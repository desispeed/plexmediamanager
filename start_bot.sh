#!/bin/bash
# Start Telegram Bot for Plex Cleanup

cd "$(dirname "$0")"

# Check if config exists
if [ ! -f "config.sh" ]; then
    echo "❌ Error: config.sh not found!"
    echo "Please create config.sh with your Plex and Telegram settings."
    exit 1
fi

# Load config
source config.sh

# Check required variables
if [ -z "$PLEX_URL" ] || [ -z "$PLEX_TOKEN" ]; then
    echo "❌ Error: PLEX_URL and PLEX_TOKEN must be set in config.sh"
    exit 1
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "❌ Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in config.sh"
    exit 1
fi

# Export environment variables for the bot
export PLEX_URL="$PLEX_URL"
export PLEX_TOKEN="$PLEX_TOKEN"
export MAX_VIEWS="$MAX_VIEWS"
export DAYS_NOT_WATCHED="$DAYS_NOT_WATCHED"
export TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
export TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID"
export SSH_HOST="$SSH_HOST"
export SSH_USER="$SSH_USER"
export REMOTE_PATH="$REMOTE_PATH"

echo "============================================"
echo "Starting Plex Cleanup Telegram Bot"
echo "============================================"
echo "Server: $PLEX_URL"
echo "Max views: $MAX_VIEWS"
if [ -n "$DAYS_NOT_WATCHED" ]; then
    echo "Time filter: $DAYS_NOT_WATCHED days"
fi
echo "Authorized Chat ID: $TELEGRAM_CHAT_ID"
echo "============================================"
echo ""
echo "✓ Bot is starting..."
echo "✓ Send /start to your bot to begin!"
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""

# Start the bot
python3 telegram_bot.py
