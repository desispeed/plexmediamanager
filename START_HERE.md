# Quick Start Guide

## Setup (First Time Only)

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
# From plex-manager root directory
npm install
```

## Running the Application

You need TWO terminal windows:

### Terminal 1 - Backend API
```bash
cd backend
./start_api.sh
```
This starts the API server on http://localhost:5000

### Terminal 2 - Frontend
```bash
# From plex-manager root directory
npm run dev
```
This starts the React app on http://localhost:5173

### Open in Browser
http://localhost:5173

## Features Available

✅ **Dashboard** - View Plex server status and quick actions
✅ **Cleanup** - Browse and select unwatched movies for deletion
✅ **Scanner** - Trigger Plex library scans
✅ **Requests** - Submit and manage media requests

## Troubleshooting

**Backend won't start?**
- Make sure you're in the backend directory
- Check that Python dependencies are installed: `pip list | grep flask`

**Frontend shows errors?**
- Make sure backend is running first
- Check that API_BASE URL in components matches your backend (http://localhost:5000/api)

**Can't connect to Plex?**
- Verify your Plex server is running
- Check config in `../plex-cleanup/config.sh`

## Next Steps

- The app is functional but delete operations are demo-only
- To enable actual deletion, integrate with the plex_cleanup.py script
- Consider adding authentication for production use
- Add qBittorrent integration (future enhancement)

Enjoy your Plex Manager! 🎬
