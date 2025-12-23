#!/usr/bin/env python3
"""
Plex Manager Backend API
Flask API for managing Plex, qBittorrent, and media requests
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()

try:
    from plex_cleanup import PlexCleanup
    from plexapi.server import PlexServer
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure plexapi is installed: pip install plexapi flask flask-cors")

try:
    from auth import auth_manager
    AUTH_ENABLED = True
except ImportError as e:
    print(f"Warning: Authentication module not available: {e}")
    AUTH_ENABLED = False

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration - Set via environment variables
PLEX_URL = os.getenv('PLEX_URL')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
MAX_VIEWS = int(os.getenv('MAX_VIEWS', '1'))
DAYS_NOT_WATCHED = int(os.getenv('DAYS_NOT_WATCHED', '30')) if os.getenv('DAYS_NOT_WATCHED') else None

# Validate required configuration
if not PLEX_URL or not PLEX_TOKEN:
    print("ERROR: PLEX_URL and PLEX_TOKEN environment variables must be set!")
    print("Copy backend/.env.example to backend/.env and configure your Plex credentials.")
    sys.exit(1)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    auth_status = 'enabled' if AUTH_ENABLED else 'disabled'
    return jsonify({
        'status': 'ok',
        'message': 'Plex Manager API is running',
        'auth': auth_status
    })


# =============================================================================
# Authentication Endpoints
# =============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user with MFA"""
    if not AUTH_ENABLED:
        return jsonify({'error': 'Authentication not enabled'}), 503

    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        totp_secret, error = auth_manager.create_user(username, password)

        if error:
            return jsonify({'error': error}), 400

        # Generate QR code for Microsoft Authenticator
        qr_code = auth_manager.generate_qr_code(username)

        return jsonify({
            'status': 'success',
            'message': 'User created. Scan QR code with Microsoft Authenticator',
            'qr_code': qr_code,
            'totp_secret': totp_secret
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/verify-totp', methods=['POST'])
def verify_totp():
    """Verify TOTP code and enable MFA"""
    if not AUTH_ENABLED:
        return jsonify({'error': 'Authentication not enabled'}), 503

    try:
        data = request.json
        username = data.get('username')
        token = data.get('token')

        if not username or not token:
            return jsonify({'error': 'Username and token required'}), 400

        if auth_manager.verify_totp(username, token):
            auth_manager.enable_totp(username)
            return jsonify({
                'status': 'success',
                'message': 'MFA enabled successfully'
            })
        else:
            return jsonify({'error': 'Invalid token'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with username, password, and MFA token"""
    if not AUTH_ENABLED:
        return jsonify({'error': 'Authentication not enabled'}), 503

    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        token = data.get('token')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        # Verify password
        if not auth_manager.verify_password(username, password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Check if MFA is enabled
        user = auth_manager.users.get(username)
        if user and user.get('totp_enabled'):
            if not token:
                return jsonify({
                    'status': 'mfa_required',
                    'message': 'MFA token required'
                }), 200

            # Verify MFA token
            if not auth_manager.verify_totp(username, token):
                return jsonify({'error': 'Invalid MFA token'}), 401

        # Generate JWT
        jwt_token = auth_manager.generate_jwt(username)

        return jsonify({
            'status': 'success',
            'token': jwt_token,
            'username': username
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    """Verify JWT token"""
    if not AUTH_ENABLED:
        return jsonify({'error': 'Authentication not enabled'}), 503

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401

    if token.startswith('Bearer '):
        token = token[7:]

    username = auth_manager.verify_jwt(token)
    if username:
        return jsonify({'valid': True, 'username': username})
    else:
        return jsonify({'valid': False}), 401


@app.route('/api/plex/status', methods=['GET'])
def plex_status():
    """Get Plex server status"""
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        return jsonify({
            'status': 'connected',
            'serverName': plex.friendlyName,
            'version': plex.version,
            'platform': plex.platform,
            'url': PLEX_URL
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/plex/movies', methods=['GET'])
def get_movies():
    """Get list of movies matching cleanup criteria"""
    try:
        max_views = int(request.args.get('max_views', MAX_VIEWS))
        days = int(request.args.get('days', DAYS_NOT_WATCHED)) if request.args.get('days') else DAYS_NOT_WATCHED

        cleanup = PlexCleanup(PLEX_URL, PLEX_TOKEN)
        movies = cleanup.get_unwatched_movies(max_view_count=max_views, days_since_watched=days)

        # Clear previous cache
        movies_cache.clear()

        # Convert to JSON-serializable format and cache plex objects
        movies_data = []
        for idx, movie in enumerate(movies):
            movie_key = f"{movie['title']}_{movie['year']}_{idx}"

            # Store plex object for later deletion
            movies_cache[movie_key] = movie['plex_object']

            movies_data.append({
                'movieKey': movie_key,
                'title': movie['title'],
                'year': movie['year'],
                'viewCount': movie['view_count'],
                'addedDate': movie['added_date'],
                'lastViewed': movie['last_viewed'],
                'filePaths': movie['file_paths'],
                'fileSizeMB': movie['file_size_mb'],
                'rating': movie['rating']
            })

        total_size_gb = sum(m['file_size_mb'] for m in movies) / 1024

        return jsonify({
            'movies': movies_data,
            'totalCount': len(movies),
            'totalSizeGB': round(total_size_gb, 2)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/plex/movies/delete', methods=['POST'])
def delete_movies():
    """Delete selected movies from Plex"""
    try:
        data = request.json
        movie_keys = data.get('movieKeys', [])

        if not movie_keys:
            return jsonify({'error': 'No movies specified'}), 400

        deleted_count = 0
        failed_count = 0
        deleted_size_mb = 0
        errors = []

        for movie_key in movie_keys:
            if movie_key not in movies_cache:
                failed_count += 1
                errors.append(f"Movie not found in cache: {movie_key}")
                continue

            try:
                plex_movie = movies_cache[movie_key]

                # Get size before deletion
                movie_size_mb = sum(media.parts[0].size for media in plex_movie.media) / (1024 * 1024)

                # Delete the movie from Plex
                plex_movie.delete()

                deleted_count += 1
                deleted_size_mb += movie_size_mb

                # Remove from cache
                del movies_cache[movie_key]

            except Exception as e:
                failed_count += 1
                errors.append(f"Failed to delete {movie_key}: {str(e)}")

        deleted_size_gb = deleted_size_mb / 1024

        return jsonify({
            'status': 'success',
            'deletedCount': deleted_count,
            'failedCount': failed_count,
            'deletedSizeGB': round(deleted_size_gb, 2),
            'errors': errors
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/plex/libraries', methods=['GET'])
def get_libraries():
    """Get list of Plex libraries"""
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        libraries = []

        for section in plex.library.sections():
            libraries.append({
                'key': section.key,
                'title': section.title,
                'type': section.type,
                'count': section.totalSize if hasattr(section, 'totalSize') else 0
            })

        return jsonify({'libraries': libraries})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/plex/scan', methods=['POST'])
def scan_library():
    """Trigger Plex library scan"""
    try:
        data = request.json
        library_key = data.get('libraryKey')

        plex = PlexServer(PLEX_URL, PLEX_TOKEN)

        if library_key:
            # Scan specific library
            section = plex.library.sectionByID(library_key)
            section.update()
            message = f"Scanning library: {section.title}"
        else:
            # Scan all libraries
            for section in plex.library.sections():
                section.update()
            message = "Scanning all libraries"

        return jsonify({'status': 'success', 'message': message})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/plex/restart', methods=['POST'])
def restart_plex():
    """Restart Plex server"""
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)

        # Try different restart endpoints
        endpoints = ['/restart', '/:/restart']
        success = False

        for endpoint in endpoints:
            try:
                plex.query(endpoint)
                success = True
                break
            except:
                continue

        if success:
            return jsonify({'status': 'success', 'message': 'Plex server restart initiated'})
        else:
            return jsonify({'error': 'Unable to restart server'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Media Request endpoints
requests_db = []  # Simple in-memory storage (use database in production)

# Movie cache for deletion (stores plex objects)
movies_cache = {}  # Format: {movie_key: plex_movie_object}


@app.route('/api/requests', methods=['GET'])
def get_requests():
    """Get all media requests"""
    return jsonify({'requests': requests_db})


@app.route('/api/requests', methods=['POST'])
def create_request():
    """Create a new media request"""
    try:
        data = request.json
        new_request = {
            'id': len(requests_db) + 1,
            'title': data.get('title'),
            'type': data.get('type', 'movie'),  # movie or tv
            'year': data.get('year'),
            'status': 'pending',
            'requestedBy': data.get('requestedBy', 'Anonymous'),
            'requestedAt': data.get('requestedAt'),
            'notes': data.get('notes', '')
        }
        requests_db.append(new_request)

        return jsonify({'status': 'success', 'request': new_request}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/requests/<int:request_id>', methods=['PATCH'])
def update_request(request_id):
    """Update request status"""
    try:
        data = request.json
        for req in requests_db:
            if req['id'] == request_id:
                req['status'] = data.get('status', req['status'])
                return jsonify({'status': 'success', 'request': req})

        return jsonify({'error': 'Request not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Get port from environment variable (Railway uses PORT)
    port = int(os.getenv('PORT', 5001))

    # Determine if we're in production (Railway sets RAILWAY_ENVIRONMENT)
    is_production = os.getenv('RAILWAY_ENVIRONMENT') is not None

    print("=" * 60)
    print("Plex Manager API Server")
    print("=" * 60)
    print(f"Environment: {'Production' if is_production else 'Development'}")
    print(f"Plex Server: {PLEX_URL}")
    print(f"API running on port: {port}")
    print("=" * 60)

    app.run(debug=not is_production, host='0.0.0.0', port=port)
