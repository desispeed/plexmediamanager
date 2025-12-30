#!/usr/bin/env python3
"""
Test script to check what disk usage info Plex API provides
"""

from plexapi.server import PlexServer
import json

PLEX_URL = "http://mirror.seedhost.eu:32108"
PLEX_TOKEN = "j89Uh7HxZfGPEj3nkq9Z"

print("Connecting to Plex server...")
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

print(f"\nServer: {plex.friendlyName}")
print(f"Version: {plex.version}")
print(f"Platform: {plex.platform}")
print(f"Platform Version: {plex.platformVersion}")

# Check for system info
print("\n" + "="*80)
print("Checking for disk/system information...")
print("="*80)

# Try to get server resources
try:
    print("\nServer attributes:")
    for attr in dir(plex):
        if not attr.startswith('_'):
            try:
                value = getattr(plex, attr)
                if not callable(value) and 'disk' in attr.lower() or 'storage' in attr.lower() or 'space' in attr.lower():
                    print(f"  {attr}: {value}")
            except:
                pass
except Exception as e:
    print(f"Error: {e}")

# Try system info
try:
    print("\nTrying system info...")
    # Some Plex servers have a systemInfo endpoint
    if hasattr(plex, 'systemInfo'):
        info = plex.systemInfo()
        print(f"System Info: {info}")
except Exception as e:
    print(f"No system info: {e}")

# Check server statistics
try:
    print("\nServer stats:")
    if hasattr(plex, 'statistics'):
        stats = plex.statistics()
        print(f"Statistics: {stats}")
except Exception as e:
    print(f"No statistics: {e}")

# Try to get all libraries and their sizes
print("\n" + "="*80)
print("Library Information:")
print("="*80)
sections = plex.library.sections()
for section in sections:
    print(f"\n{section.title} ({section.type}):")
    print(f"  UUID: {section.uuid}")
    print(f"  Key: {section.key}")
    print(f"  Total items: {section.totalSize if hasattr(section, 'totalSize') else 'Unknown'}")

    # Check section attributes
    for attr in ['totalSize', 'size', 'diskSize', 'storage']:
        if hasattr(section, attr):
            print(f"  {attr}: {getattr(section, attr)}")

# Check transient token and try direct API call
print("\n" + "="*80)
print("Trying direct API endpoints...")
print("="*80)

try:
    import requests

    # Try servers endpoint
    url = f"{PLEX_URL}/servers?X-Plex-Token={PLEX_TOKEN}"
    print(f"\nTrying: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        print("Response received (truncated):")
        print(response.text[:500])

    # Try status endpoint
    url = f"{PLEX_URL}/status/sessions?X-Plex-Token={PLEX_TOKEN}"
    print(f"\nTrying: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        print("Sessions endpoint works")

    # Try devices endpoint
    url = f"{PLEX_URL}/?X-Plex-Token={PLEX_TOKEN}"
    print(f"\nTrying root endpoint...")
    response = requests.get(url)
    if response.status_code == 200:
        print("Root endpoint response (first 1000 chars):")
        print(response.text[:1000])

except Exception as e:
    print(f"Error with API calls: {e}")

print("\n" + "="*80)
print("Test complete!")
print("="*80)
