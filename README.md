# Plex Manager

A modern web application for managing your Plex Media Server with features for cleanup, library scanning, and media requests.

🌐 **Live Demo**: [mediamanagerdx.com](https://mediamanagerdx.com)

## Features

- **Dashboard**: View Plex server status and quick actions
- **Media Cleanup**: Browse and delete unwatched movies to free up space
- **Library Scanner**: Trigger Plex library scans
- **Media Requests**: Submit and manage media requests
- **Mobile/Desktop Modes**: Auto-detecting responsive layouts with manual toggle
- **Live Deployment**: Frontend on Vercel, Backend on Railway

## Tech Stack

- **Frontend**: React + Vite (deployed on Vercel)
- **Backend**: Flask (Python) (deployed on Railway)
- **APIs**: PlexAPI for Plex integration

## Deployment

### Backend Deployment (Railway)

1. **Sign up for Railway**
   - Go to [railway.app](https://railway.app)
   - Sign in with your GitHub account

2. **Create New Project**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select this repository
   - Railway auto-detects the Python app

3. **Configure Environment Variables**

   In Railway Dashboard → Variables tab, add:
   ```
   PLEX_URL=http://your-plex-server:32400
   PLEX_TOKEN=your-plex-token-here
   MAX_VIEWS=1
   DAYS_NOT_WATCHED=30
   ```

4. **Get Your API URL**
   - Go to Settings → Generate Domain
   - Copy the URL (e.g., `https://your-app.railway.app`)

### Frontend Deployment (Vercel)

1. **Deploy to Vercel**
   - Connect your GitHub repo to Vercel
   - Vercel auto-detects the Vite app

2. **Configure Environment Variable**

   In Vercel Dashboard → Settings → Environment Variables:
   ```
   VITE_API_BASE=https://your-railway-url.railway.app/api
   ```

3. **Redeploy**
   - Trigger a new deployment for changes to take effect

## Local Development

### Backend (Local)

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your Plex credentials
```

3. Start the backend:
```bash
python3 api.py
```

API runs on `http://localhost:5001`

### Frontend (Local)

1. Install Node dependencies:
```bash
npm install
```

2. Set environment variable:
```bash
# Create .env.local
echo "VITE_API_BASE=http://localhost:5001/api" > .env.local
```

3. Start development server:
```bash
npm run dev
```

App runs on `http://localhost:5173`

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/plex/status` - Get Plex server status
- `GET /api/plex/movies` - Get movies matching cleanup criteria
- `POST /api/plex/movies/delete` - Delete selected movies
- `GET /api/plex/libraries` - Get list of libraries
- `POST /api/plex/scan` - Trigger library scan
- `POST /api/plex/restart` - Restart Plex server
- `GET /api/requests` - Get media requests
- `POST /api/requests` - Create media request
- `PATCH /api/requests/:id` - Update request status

## Configuration

### Environment Variables

- `PLEX_URL` - Your Plex server URL (e.g., `http://192.168.1.100:32400`)
- `PLEX_TOKEN` - Your Plex authentication token
- `MAX_VIEWS` - Maximum view count for cleanup (default: 1)
- `DAYS_NOT_WATCHED` - Days since last watched (default: 30)

### Getting Your Plex Token

1. Log into Plex Web App
2. Open any movie/show
3. Click "..." → "Get Info" → "View XML"
4. Look at the URL - the token is the `X-Plex-Token` parameter
5. Example: `https://app.plex.tv/...?X-Plex-Token=YOUR_TOKEN_HERE`

Or use this XML method:
```bash
# In browser, visit and sign in:
https://plex.tv/devices.xml
# Find your server and copy the token attribute
```

## Architecture

```
┌─────────────┐      HTTPS       ┌──────────────┐
│   Vercel    │ ───────────────> │   Railway    │
│  (Frontend) │                  │  (Backend)   │
│  React App  │ <─────────────── │  Flask API   │
└─────────────┘      JSON        └──────────────┘
                                         │
                                         │ PlexAPI
                                         ▼
                                  ┌──────────────┐
                                  │  Plex Server │
                                  │   (Remote)   │
                                  └──────────────┘
```

## Features in Detail

### Media Cleanup
- Filter movies by view count and last watched date
- Select multiple movies for batch deletion
- Real-time storage calculation
- Double confirmation for safety
- Desktop: Table view | Mobile: Card view

### Library Scanner
- Scan all libraries or individual ones
- Refresh metadata
- Quick actions from dashboard

### Media Requests
- Submit requests for movies/TV shows
- Track request status (pending/approved/completed)
- Admin can approve/reject requests
- In-memory storage (resets on restart)

### Mode Toggle
- Auto-detects mobile/desktop
- Manual override available
- Saves preference in localStorage
- Optimized layouts for each mode

## Security Warning

⚠️ **Important**:
- Never commit your Plex token or credentials to version control
- Use environment variables for sensitive data
- The `.env` file is excluded in `.gitignore`
- Consider adding authentication before exposing publicly
- This app has full delete permissions - protect the URL!

## Contributing

Pull requests welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a PR

## Support

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones

## License

MIT
