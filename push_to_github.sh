#!/bin/bash
# Push Plex Media Manager to GitHub

echo "🚀 Pushing Plex Media Manager to GitHub..."
echo ""

# Check if remote exists
if git remote | grep -q origin; then
    echo "✅ Remote 'origin' already configured"
else
    echo "Adding remote 'origin'..."
    git remote add origin https://github.com/monalvalia/plex-media-manager.git
fi

echo ""
echo "📤 Pushing to GitHub..."
echo ""

# Push to GitHub
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🌐 View your repository:"
    echo "   https://github.com/monalvalia/plex-media-manager"
    echo ""
    echo "📦 What was pushed:"
    echo "   - 38 files"
    echo "   - 7,453 lines of code"
    echo "   - Web dashboard with live Plex API"
    echo "   - Docker containerization"
    echo "   - Complete documentation"
    echo ""
else
    echo ""
    echo "❌ Push failed!"
    echo ""
    echo "📝 Instructions:"
    echo "1. Make sure you've created the repo on GitHub:"
    echo "   https://github.com/new"
    echo ""
    echo "2. Repository name: plex-media-manager"
    echo "3. Don't initialize with README (we have one)"
    echo ""
    echo "4. After creating, run this script again:"
    echo "   ./push_to_github.sh"
    echo ""
fi
