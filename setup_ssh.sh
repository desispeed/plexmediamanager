#!/bin/bash
# Setup SSH access to seedbox

SEEDBOX="mirror.seedhost.eu"

echo "================================================================================"
echo "SEEDBOX SSH SETUP"
echo "================================================================================"
echo ""
echo "Setting up SSH access to: ${SEEDBOX}"
echo ""

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa.pub ] && [ ! -f ~/.ssh/id_ed25519.pub ]; then
    echo "No SSH key found. Generating new SSH key..."
    read -p "Enter your email for SSH key: " email
    ssh-keygen -t ed25519 -C "$email"
fi

# Copy SSH key
echo ""
echo "Copying SSH key to seedbox..."
echo "You will be prompted for your seedbox password."
echo ""

if [ -f ~/.ssh/id_ed25519.pub ]; then
    ssh-copy-id -i ~/.ssh/id_ed25519.pub "${SEEDBOX}"
elif [ -f ~/.ssh/id_rsa.pub ]; then
    ssh-copy-id -i ~/.ssh/id_rsa.pub "${SEEDBOX}"
fi

# Test connection
echo ""
echo "Testing SSH connection..."
if ssh -o ConnectTimeout=5 "${SEEDBOX}" "echo 'SSH connection successful!'" 2>/dev/null; then
    echo "✓ SSH setup complete!"
    echo ""
    echo "You can now run: ./scan_seedbox_space.sh"
else
    echo "❌ SSH connection failed. Please check your credentials."
fi

echo ""
echo "================================================================================"
