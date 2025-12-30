#!/bin/bash
# Plex Cleanup Configuration
# Copy this to config.sh and fill in your details

# Plex Server URL (include http:// or https://)
PLEX_URL="http://192.168.1.100:32400"

# Plex Token
# To get your token:
# 1. Open Plex Web App
# 2. Play any media
# 3. Click the "..." menu > "Get Info" > "View XML"
# 4. Look for X-Plex-Token in the URL
PLEX_TOKEN="your_plex_token_here"

# Maximum view count (delete movies with this many views or less)
MAX_VIEWS=1

# Time-based filter: Only delete movies not watched in last X days
# Set to empty to disable time filter and use view count only
DAYS_NOT_WATCHED=30

# Telegram Notifications (optional)
# Get bot token from @BotFather on Telegram
# Get chat ID by messaging @userinfobot or @getidsbot
TELEGRAM_BOT_TOKEN=""
TELEGRAM_CHAT_ID=""
# Set to "yes" to enable Telegram notifications
ENABLE_TELEGRAM="no"
