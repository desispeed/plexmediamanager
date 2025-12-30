#!/bin/bash
# Quick cleanup script with interactive setup

cd "$(dirname "$0")"

# Check if config exists
if [ ! -f "config.sh" ]; then
    echo "⚠️  No config.sh found!"
    echo ""
    echo "Setting up configuration..."
    echo ""

    # Prompt for Plex URL
    read -p "Enter your Plex server URL (e.g., http://192.168.1.100:32400): " plex_url

    # Prompt for token
    echo ""
    echo "To get your Plex token:"
    echo "1. Open Plex Web App"
    echo "2. Play any movie"
    echo "3. Click '...' menu > 'Get Info' > 'View XML'"
    echo "4. Copy the X-Plex-Token value from the URL"
    echo ""
    read -p "Enter your Plex token: " plex_token

    # Create config
    cat > config.sh << EOF
#!/bin/bash
# Plex Cleanup Configuration

PLEX_URL="$plex_url"
PLEX_TOKEN="$plex_token"
MAX_VIEWS=1
EOF

    chmod +x config.sh
    echo "✓ Config saved to config.sh"
    echo ""
fi

# Load config
source config.sh

echo "============================================"
echo "Plex Movie Cleanup Tool"
echo "============================================"
echo "Server: $PLEX_URL"
echo "Max views: $MAX_VIEWS"
if [ -n "$DAYS_NOT_WATCHED" ]; then
    echo "Time filter: Not watched in last $DAYS_NOT_WATCHED days"
fi
if [ "$ENABLE_TELEGRAM" = "yes" ]; then
    echo "Telegram: Enabled"
fi
echo "============================================"
echo ""

# Build Telegram arguments
TELEGRAM_ARGS=""
if [ "$ENABLE_TELEGRAM" = "yes" ] && [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    TELEGRAM_ARGS="--telegram-token $TELEGRAM_BOT_TOKEN --telegram-chat-id $TELEGRAM_CHAT_ID --send-telegram"
fi

# Build SSH arguments
SSH_ARGS=""
if [ -n "$SSH_HOST" ] && [ -n "$SSH_USER" ]; then
    SSH_ARGS="--ssh-host $SSH_HOST --ssh-user $SSH_USER --remote-path $REMOTE_PATH"
fi

# Ask what to do
echo "What would you like to do?"
echo "1) Preview movies that would be deleted (dry-run)"
echo "2) Delete movies (with confirmation)"
echo "3) Analyze storage usage (Plex media)"
echo "4) Check disk usage (actual filesystem)"
echo "5) Exit"
echo ""
read -p "Choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "Running in DRY-RUN mode (preview only)..."
        if [ -n "$DAYS_NOT_WATCHED" ]; then
            python3 plex_cleanup.py --url "$PLEX_URL" --token "$PLEX_TOKEN" --max-views $MAX_VIEWS --days $DAYS_NOT_WATCHED --dry-run $TELEGRAM_ARGS
        else
            python3 plex_cleanup.py --url "$PLEX_URL" --token "$PLEX_TOKEN" --max-views $MAX_VIEWS --dry-run $TELEGRAM_ARGS
        fi
        ;;
    2)
        echo ""
        echo "Running in DELETE mode (will ask for confirmation)..."
        if [ -n "$DAYS_NOT_WATCHED" ]; then
            python3 plex_cleanup.py --url "$PLEX_URL" --token "$PLEX_TOKEN" --max-views $MAX_VIEWS --days $DAYS_NOT_WATCHED $TELEGRAM_ARGS
        else
            python3 plex_cleanup.py --url "$PLEX_URL" --token "$PLEX_TOKEN" --max-views $MAX_VIEWS $TELEGRAM_ARGS
        fi
        ;;
    3)
        echo ""
        echo "Analyzing storage usage..."
        python3 plex_cleanup.py --url "$PLEX_URL" --token "$PLEX_TOKEN" --analyze-storage $SSH_ARGS $TELEGRAM_ARGS
        ;;
    4)
        echo ""
        echo "Checking disk usage..."
        python3 plex_cleanup.py --url "$PLEX_URL" --token "$PLEX_TOKEN" --check-disk $SSH_ARGS $TELEGRAM_ARGS
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac
