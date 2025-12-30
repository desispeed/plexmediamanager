#!/bin/bash
# Test Plex restart manually

cd "$(dirname "$0")"

echo "============================================"
echo "Testing Plex Restart"
echo "============================================"
echo ""

python3 restart_plex.py

echo ""
echo "============================================"
echo "Check the output above to verify the restart"
echo "View full logs: tail -f plex_restart.log"
echo "============================================"
