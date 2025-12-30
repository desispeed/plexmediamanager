#!/usr/bin/env python3
"""
Plex Media Manager - Web Application
Flask web server with API endpoints for live Plex data
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import sys
import os

# Add parent directory to path to import plex modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plexapi.server import PlexServer
from storage_analyzer import StorageAnalyzer
from disk_utils import DiskUsage

app = Flask(__name__,
            static_folder='.',
            static_url_path='',
            template_folder='.')
CORS(app)

# Load Plex configuration
PLEX_URL = os.getenv('PLEX_URL', 'http://mirror.seedhost.eu:32108')
PLEX_TOKEN = os.getenv('PLEX_TOKEN', 'j89Uh7HxZfGPEj3nkq9Z')
TOTAL_CAPACITY_GB = float(os.getenv('TOTAL_CAPACITY_GB', '3700'))

# SSH Configuration
SSH_HOST = os.getenv('SSH_HOST', 'mirror.seedhost.eu')
SSH_USER = os.getenv('SSH_USER', 'desispeed')
REMOTE_PATH = os.getenv('REMOTE_PATH', '/home32')

def get_plex_server():
    """Connect to Plex server"""
    try:
        return PlexServer(PLEX_URL, PLEX_TOKEN)
    except Exception as e:
        print(f"Error connecting to Plex: {e}")
        return None

@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory('.', 'index.html')

@app.route('/api/stats')
def get_stats():
    """Get overall Plex statistics"""
    try:
        plex = get_plex_server()
        if not plex:
            return jsonify({'error': 'Could not connect to Plex server'}), 500

        analyzer = StorageAnalyzer(plex, TOTAL_CAPACITY_GB)
        stats = analyzer.analyze_storage()

        # Get stats for movies and TV shows (category is the key itself)
        movie_stats = stats['folder_stats'].get('Movies', {'count': 0, 'size_gb': 0})
        tv_stats = stats['folder_stats'].get('TV Shows', {'count': 0, 'size_gb': 0})

        # Calculate free percentage
        free_percentage = 100 - stats['used_percentage']

        summary = {
            'total_movies': movie_stats['count'],
            'total_movies_size_gb': round(movie_stats['size_gb'], 2),
            'total_tv_shows': tv_stats['count'],
            'total_tv_shows_size_gb': round(tv_stats['size_gb'], 2),
            'storage_used_gb': round(stats['total_used_gb'], 2),
            'storage_capacity_gb': TOTAL_CAPACITY_GB,
            'storage_used_percent': round(stats['used_percentage'], 1),
            'storage_available_gb': round(stats['free_gb'], 2),
            'storage_available_percent': round(free_percentage, 1)
        }

        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/storage')
def get_storage():
    """Get detailed storage breakdown"""
    try:
        plex = get_plex_server()
        if not plex:
            return jsonify({'error': 'Could not connect to Plex server'}), 500

        analyzer = StorageAnalyzer(plex, TOTAL_CAPACITY_GB)
        stats = analyzer.analyze_storage()

        # Format storage breakdown (folder_name IS the category)
        breakdown = []
        for category_name, folder_stats in stats['folder_stats'].items():
            # Calculate percentages
            percent_of_total = (folder_stats['size_gb'] / TOTAL_CAPACITY_GB) * 100 if TOTAL_CAPACITY_GB > 0 else 0
            percent_of_used = (folder_stats['size_gb'] / stats['total_used_gb']) * 100 if stats['total_used_gb'] > 0 else 0

            breakdown.append({
                'category': category_name,
                'files': folder_stats['count'],
                'size_gb': round(folder_stats['size_gb'], 2),
                'percent_of_total': round(percent_of_total, 1),
                'percent_of_used': round(percent_of_used, 1)
            })

        return jsonify({
            'total_files': sum(s['count'] for s in stats['folder_stats'].values()),
            'total_used_gb': round(stats['total_used_gb'], 2),
            'capacity_gb': TOTAL_CAPACITY_GB,
            'used_percentage': round(stats['used_percentage'], 1),
            'available_gb': round(stats['free_gb'], 2),
            'breakdown': breakdown
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup-candidates')
def get_cleanup_candidates():
    """Get list of movies that can be deleted"""
    try:
        plex = get_plex_server()
        if not plex:
            return jsonify({'error': 'Could not connect to Plex server'}), 500

        max_view_count = int(request.args.get('max_view_count', 1))
        days_not_watched = int(request.args.get('days_not_watched', 30))

        candidates = []
        total_size_gb = 0

        # Scan movie libraries
        for section in plex.library.sections():
            if section.type != 'movie':
                continue

            for movie in section.all():
                if movie.viewCount is None or movie.viewCount <= max_view_count:
                    # Calculate days since last watched
                    days_since_watched = None
                    if movie.lastViewedAt:
                        from datetime import datetime
                        days_since_watched = (datetime.now() - movie.lastViewedAt).days

                    # Check if it meets criteria
                    if days_since_watched is None or days_since_watched >= days_not_watched:
                        size_gb = sum(part.size for part in movie.media[0].parts if hasattr(part, 'size')) / (1024**3)
                        candidates.append({
                            'title': movie.title,
                            'year': movie.year,
                            'size_gb': round(size_gb, 1),
                            'view_count': movie.viewCount or 0,
                            'last_viewed': movie.lastViewedAt.strftime('%Y-%m-%d') if movie.lastViewedAt else 'Never',
                            'days_since_watched': days_since_watched
                        })
                        total_size_gb += size_gb

        # Sort by size (largest first)
        candidates.sort(key=lambda x: x['size_gb'], reverse=True)

        return jsonify({
            'total_candidates': len(candidates),
            'total_size_gb': round(total_size_gb, 2),
            'candidates': candidates[:100]  # Return top 100
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/disk-usage')
def get_disk_usage():
    """Get actual disk usage from filesystem"""
    try:
        disk_checker = DiskUsage(SSH_HOST, SSH_USER)
        usage = disk_checker.get_disk_usage(prefer_remote=True, remote_path=REMOTE_PATH)

        if not usage:
            return jsonify({'error': 'Could not retrieve disk usage'}), 500

        return jsonify({
            'total_gb': round(usage['total_gb'], 2),
            'used_gb': round(usage['used_gb'], 2),
            'free_gb': round(usage['free_gb'], 2),
            'percent_used': round(usage['percent'], 1),
            'source': usage.get('source', 'unknown')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or update cleanup settings"""
    if request.method == 'GET':
        return jsonify({
            'max_view_count': 1,
            'days_not_watched': 30,
            'plex_url': PLEX_URL,
            'capacity_gb': TOTAL_CAPACITY_GB
        })
    else:
        # TODO: Implement settings update
        return jsonify({'success': True})

@app.route('/styles.css')
def serve_css():
    """Serve CSS file"""
    return send_from_directory('.', 'styles.css')

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"🚀 Starting Plex Media Manager Web Server")
    print(f"📡 Plex Server: {PLEX_URL}")
    print(f"🌐 Web Interface: http://localhost:{port}")
    print(f"📊 API Endpoints:")
    print(f"   - GET  /api/stats              - Overall statistics")
    print(f"   - GET  /api/storage            - Storage breakdown")
    print(f"   - GET  /api/cleanup-candidates - Cleanup candidates")
    print(f"   - GET  /api/disk-usage         - Disk usage")
    print(f"   - GET  /api/settings           - Settings")
    print()

    app.run(host='0.0.0.0', port=port, debug=debug)
