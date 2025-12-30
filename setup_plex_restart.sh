#!/bin/bash
# Setup automatic Plex restart at 4am CST daily

cd "$(dirname "$0")"

echo "============================================"
echo "Plex Automatic Restart Setup"
echo "============================================"
echo ""

# Check if LaunchAgents directory exists
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo "Creating LaunchAgents directory..."
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

PLIST_SOURCE="com.plex.restart.plist"
PLIST_DEST="$LAUNCH_AGENTS_DIR/com.plex.restart.plist"

# Check if already installed
if [ -f "$PLIST_DEST" ]; then
    echo "⚠️  Plex restart job already installed."
    echo "Unloading existing job..."
    launchctl unload "$PLIST_DEST" 2>/dev/null
fi

# Copy plist file
echo "Installing launchd job..."
cp "$PLIST_SOURCE" "$PLIST_DEST"

# Load the job
echo "Loading job..."
launchctl load "$PLIST_DEST"

# Verify
if launchctl list | grep -q "com.plex.restart"; then
    echo ""
    echo "✅ Success! Plex will restart daily at 4:00 AM"
    echo ""
    echo "Configuration:"
    echo "  - Time: 4:00 AM (system local time)"
    echo "  - Logs: $PWD/plex_restart.log"
    echo "  - Errors: $PWD/plex_restart_error.log"
    echo ""
    echo "Commands:"
    echo "  Test now:    ./test_plex_restart.sh"
    echo "  View logs:   tail -f plex_restart.log"
    echo "  Uninstall:   ./uninstall_plex_restart.sh"
else
    echo ""
    echo "❌ Failed to load job. Check for errors above."
    exit 1
fi

echo "============================================"
