# Plex Manager

A modern web application for managing your Plex Media Server with features for cleanup, library scanning, and media requests.

## Features

- **Dashboard**: View Plex server status and quick actions
- **Media Cleanup**: Browse and delete unwatched movies to free up space
- **Library Scanner**: Trigger Plex library scans
- **Media Requests**: Submit and manage media requests

## Tech Stack

- **Frontend**: React + Vite
- **Backend**: Flask (Python)
- **APIs**: PlexAPI for Plex integration

## Setup

### Backend

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Configure Plex settings in `backend/api.py`:
   - Set `PLEX_URL` and `PLEX_TOKEN` environment variables
   - Or modify the defaults in the code

3. Start the backend:
```bash
python3 api.py
```

The API will run on `http://localhost:5001`

### Frontend

1. Install Node dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will run on `http://localhost:5173`

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

Set environment variables:
- `PLEX_URL` - Your Plex server URL
- `PLEX_TOKEN` - Your Plex authentication token
- `MAX_VIEWS` - Maximum view count for cleanup (default: 1)
- `DAYS_NOT_WATCHED` - Days since last watched (default: 30)

## Security Warning

⚠️ **Important**: Never commit your Plex token or credentials to version control. Use environment variables or a separate config file that's excluded in `.gitignore`.

## License

MIT
