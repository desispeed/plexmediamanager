#!/usr/bin/env python3
"""
Detailed storage analysis using Plex API with file path inspection
"""

import sys
import os
from collections import defaultdict
from plexapi.server import PlexServer

# Server config
PLEX_URL = "http://mirror.seedhost.eu:32108"
PLEX_TOKEN = "j89Uh7HxZfGPEj3nkq9Z"
TOTAL_SPACE_GB = 3700
BASE_PATH = "/home32/desispeed/Downloads"

def categorize_path(file_path):
    """Categorize file by folder structure"""
    if not file_path:
        return "Unknown"

    # Normalize path
    path_lower = file_path.lower()

    # Check base folders
    if 'movie' in path_lower:
        return "Movies"
    elif 'tv' in path_lower or 'show' in path_lower or 'series' in path_lower:
        return "TV Shows"
    elif 'music' in path_lower or 'audio' in path_lower:
        return "Music"
    elif 'training' in path_lower or 'course' in path_lower:
        return "Training Videos"
    elif 'software' in path_lower or 'app' in path_lower or 'program' in path_lower:
        return "Software"
    else:
        # Try to get the first folder after base path
        if BASE_PATH in file_path:
            relative = file_path.replace(BASE_PATH, '').strip('/')
            parts = relative.split('/')
            if parts:
                return parts[0]
        return "Other"

def main():
    print("=" * 100)
    print("DETAILED PLEX STORAGE ANALYSIS")
    print("=" * 100)
    print(f"\nConnecting to Plex server: {PLEX_URL}")

    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        print(f"✓ Connected to: {plex.friendlyName}\n")

        # Get all library sections
        sections = plex.library.sections()

        folder_stats = defaultdict(lambda: {'size_gb': 0, 'count': 0, 'paths': set()})
        library_stats = {}
        file_paths_sample = []

        print("Scanning all libraries for file paths and sizes...")
        print("-" * 100)

        for section in sections:
            print(f"\n📁 {section.title} ({section.type})")

            try:
                items = section.all()
                section_size = 0
                item_count = 0

                for item in items:
                    item_count += 1

                    try:
                        # For TV shows, get episodes
                        if section.type == 'show':
                            for episode in item.episodes():
                                for media in episode.media:
                                    for part in media.parts:
                                        if hasattr(part, 'file') and hasattr(part, 'size') and part.size:
                                            file_path = part.file
                                            size = part.size
                                            section_size += size

                                            # Categorize by path
                                            category = categorize_path(file_path)
                                            folder_stats[category]['size_gb'] += size / (1024**3)
                                            folder_stats[category]['count'] += 1
                                            folder_stats[category]['paths'].add(os.path.dirname(file_path))

                                            # Sample paths
                                            if len(file_paths_sample) < 5:
                                                file_paths_sample.append(file_path)

                        # For movies and music
                        elif hasattr(item, 'media'):
                            for media in item.media:
                                for part in media.parts:
                                    if hasattr(part, 'file') and hasattr(part, 'size') and part.size:
                                        file_path = part.file
                                        size = part.size
                                        section_size += size

                                        # Categorize by path
                                        category = categorize_path(file_path)
                                        folder_stats[category]['size_gb'] += size / (1024**3)
                                        folder_stats[category]['count'] += 1
                                        folder_stats[category]['paths'].add(os.path.dirname(file_path))

                                        # Sample paths
                                        if len(file_paths_sample) < 5:
                                            file_paths_sample.append(file_path)

                        # For music artists/albums
                        elif section.type == 'artist':
                            for album in item.albums():
                                for track in album.tracks():
                                    for media in track.media:
                                        for part in media.parts:
                                            if hasattr(part, 'file') and hasattr(part, 'size') and part.size:
                                                file_path = part.file
                                                size = part.size
                                                section_size += size

                                                category = categorize_path(file_path)
                                                folder_stats[category]['size_gb'] += size / (1024**3)
                                                folder_stats[category]['count'] += 1
                                                folder_stats[category]['paths'].add(os.path.dirname(file_path))

                                                if len(file_paths_sample) < 5:
                                                    file_paths_sample.append(file_path)

                    except Exception as e:
                        continue

                section_size_gb = section_size / (1024**3)
                library_stats[section.title] = {
                    'type': section.type,
                    'size_gb': section_size_gb,
                    'count': item_count
                }

                print(f"   ✓ Scanned {item_count} items, {section_size_gb:.2f} GB")

            except Exception as e:
                print(f"   ✗ Error: {e}")

        # Show sample file paths
        if file_paths_sample:
            print("\n" + "=" * 100)
            print("SAMPLE FILE PATHS (for reference):")
            print("=" * 100)
            for path in file_paths_sample[:5]:
                print(f"  {path}")

        # Calculate total
        total_plex_gb = sum(stats['size_gb'] for stats in folder_stats.values())

        # Breakdown by folder
        print("\n" + "=" * 100)
        print("STORAGE BREAKDOWN BY FOLDER/CATEGORY")
        print("=" * 100)
        print(f"{'Category':<25} {'Files':<10} {'Size (GB)':<15} {'% of Total':<12} {'% of Used':<10}")
        print("-" * 100)

        sorted_folders = sorted(folder_stats.items(), key=lambda x: x[1]['size_gb'], reverse=True)

        for category, stats in sorted_folders:
            if stats['size_gb'] > 0:
                pct_total = (stats['size_gb'] / TOTAL_SPACE_GB * 100) if TOTAL_SPACE_GB > 0 else 0
                pct_used = (stats['size_gb'] / total_plex_gb * 100) if total_plex_gb > 0 else 0
                print(f"{category:<25} {stats['count']:<10} {stats['size_gb']:<15.2f} {pct_total:<12.1f} {pct_used:<10.1f}")

        # Show unique paths per category
        print("\n" + "=" * 100)
        print("FOLDER LOCATIONS:")
        print("=" * 100)
        for category, stats in sorted_folders:
            if stats['size_gb'] > 0:
                print(f"\n{category}:")
                for path in sorted(list(stats['paths']))[:3]:  # Show first 3 paths
                    print(f"  • {path}")
                if len(stats['paths']) > 3:
                    print(f"  ... and {len(stats['paths']) - 3} more locations")

        # Overall summary
        free_space_gb = TOTAL_SPACE_GB - total_plex_gb
        used_percentage = (total_plex_gb / TOTAL_SPACE_GB * 100) if TOTAL_SPACE_GB > 0 else 0
        free_percentage = 100 - used_percentage

        print("\n" + "=" * 100)
        print("OVERALL STORAGE SUMMARY")
        print("=" * 100)
        print(f"Total Capacity:          {TOTAL_SPACE_GB:>10.2f} GB  (100%)")
        print(f"Used by Plex Media:      {total_plex_gb:>10.2f} GB  ({used_percentage:.1f}%)")
        print(f"Free / Other:            {free_space_gb:>10.2f} GB  ({free_percentage:.1f}%)")
        print("=" * 100)

        # Visual bar
        bar_width = 80

        # Calculate proportions for each category
        bars = []
        for category, stats in sorted_folders:
            if stats['size_gb'] > 0:
                blocks = int((stats['size_gb'] / TOTAL_SPACE_GB) * bar_width)
                if blocks > 0:
                    bars.append((category, blocks, stats['size_gb']))

        # Sort by size
        bars.sort(key=lambda x: x[2], reverse=True)

        print("\nStorage Visualization:")
        print("┌" + "─" * bar_width + "┐")

        used_blocks = int((total_plex_gb / TOTAL_SPACE_GB) * bar_width)
        free_blocks = bar_width - used_blocks
        print("│" + "█" * used_blocks + "░" * free_blocks + "│")
        print("└" + "─" * bar_width + "┘")

        # Legend
        print("\nBreakdown:")
        for category, blocks, size_gb in bars[:5]:  # Top 5
            pct = (size_gb / TOTAL_SPACE_GB * 100)
            bar = "█" * min(blocks, 40)
            print(f"  {category:<20} {bar} {size_gb:>8.2f} GB ({pct:.1f}%)")

        print(f"  {'Free/Other':<20} {'░' * min(free_blocks, 40)} {free_space_gb:>8.2f} GB ({free_percentage:.1f}%)")

        # Warnings
        if used_percentage > 90:
            print("\n⚠️  WARNING: Storage is over 90% full!")
        elif used_percentage > 80:
            print("\n⚠️  CAUTION: Storage is over 80% full")

        print("\n" + "=" * 100)
        print("NOTE: 'Free/Other' includes non-Plex files (downloads, software, etc.)")
        print("=" * 100)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
