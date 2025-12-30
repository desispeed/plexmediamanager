#!/bin/bash
# Uninstall automatic Plex restart

PLIST_FILE="$HOME/Library/LaunchAgents/com.plex.restart.plist"

echo "============================================"
echo "Uninstalling Plex Automatic Restart"
echo "============================================"
echo ""

if [ -f "$PLIST_FILE" ]; then
    echo "Unloading job..."
    launchctl unload "$PLIST_FILE"

    echo "Removing plist file..."
    rm "$PLIST_FILE"

    echo ""
    echo "✅ Plex automatic restart has been removed."
else
    echo "⚠️  Plex restart job not found."
fi

echo "============================================"
