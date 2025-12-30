#!/bin/bash
# Scan seedbox storage usage

SEEDBOX_HOST="mirror.seedhost.eu"
SEEDBOX_PATH="/home32/desispeed/Downloads"

echo "================================================================================"
echo "SEEDBOX STORAGE ANALYSIS"
echo "================================================================================"
echo ""
echo "Scanning: ${SEEDBOX_HOST}:${SEEDBOX_PATH}"
echo ""

# Check SSH connection
echo "Testing SSH connection..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "${SEEDBOX_HOST}" "echo 'Connected'" 2>/dev/null; then
    echo "⚠️  SSH key authentication not set up. Will use password authentication."
    echo ""
fi

echo ""
echo "Calculating folder sizes (this may take a few minutes)..."
echo "--------------------------------------------------------------------------------"
echo ""

# Get detailed folder sizes from Downloads directory
echo "📁 Folders in ${SEEDBOX_PATH}:"
ssh "${SEEDBOX_HOST}" "cd '${SEEDBOX_PATH}' && du -sh */ 2>/dev/null | sort -rh"

echo ""
echo "--------------------------------------------------------------------------------"
echo "DETAILED BREAKDOWN:"
echo "--------------------------------------------------------------------------------"

# Get total usage of Downloads folder
TOTAL=$(ssh "${SEEDBOX_HOST}" "du -sh '${SEEDBOX_PATH}' 2>/dev/null | cut -f1")
echo "Total Downloads folder: ${TOTAL}"

# Get disk quota/usage for the entire account
echo ""
echo "Overall Account Storage:"
ssh "${SEEDBOX_HOST}" "df -h /home32 2>/dev/null | tail -1 | awk '{print \"  Total: \" \$2 \"\\n  Used:  \" \$3 \" (\" \$5 \")\\n  Free:  \" \$4}'"

# Try to get more detailed breakdown
echo ""
echo "Top 20 largest folders:"
ssh "${SEEDBOX_HOST}" "du -h '${SEEDBOX_PATH}' 2>/dev/null | sort -rh | head -20"

echo ""
echo "================================================================================"
echo "Analysis complete!"
echo "================================================================================"
