#!/usr/bin/env python3
"""
Restart Plex Server via API
"""

import os
import sys
import logging
from datetime import datetime

try:
    from plexapi.server import PlexServer
except ImportError:
    print("Error: plexapi library not installed")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment or hardcoded
PLEX_URL = os.getenv('PLEX_URL', 'http://mirror.seedhost.eu:32108')
PLEX_TOKEN = os.getenv('PLEX_TOKEN', 'j89Uh7HxZfGPEj3nkq9Z')


def restart_plex_server():
    """Restart Plex server via API"""
    try:
        logger.info(f"Connecting to Plex server at {PLEX_URL}")
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)

        logger.info(f"Connected to: {plex.friendlyName}")
        logger.info(f"Server version: {plex.version}")
        logger.info(f"Server platform: {plex.platform}")

        # Try different restart methods
        restart_endpoints = [
            '/:/restart',
            '/:/restart?X-Plex-Token=' + PLEX_TOKEN,
            '/restart',
        ]

        for endpoint in restart_endpoints:
            try:
                logger.info(f"Trying restart endpoint: {endpoint}")
                plex.query(endpoint)
                logger.info("✓ Plex server restart command sent successfully!")
                return True
            except Exception as e:
                logger.warning(f"  Endpoint {endpoint} failed: {e}")
                continue

        # If all endpoints fail, try the session terminate approach
        logger.info("Standard restart failed. Checking if server supports restart...")

        # Check server capabilities
        try:
            # Get server identity
            identity = plex.query('/identity')
            logger.info(f"Server identity retrieved: {identity}")
        except:
            pass

        logger.error("Unable to restart server - remote server may not allow API restarts")
        logger.info("Note: Some managed/seedbox Plex servers disable restart via API for security")
        return False

    except Exception as e:
        logger.error(f"Failed to restart Plex server: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Plex Server Automatic Restart")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info("=" * 60)

    success = restart_plex_server()
    sys.exit(0 if success else 1)
