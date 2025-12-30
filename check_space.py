#!/usr/bin/env python3
"""
Calculate storage breakdown across Plex libraries
"""

import sys
from plexapi.server import PlexServer

# Server config
PLEX_URL = "http://mirror.seedhost.eu:32108"
PLEX_TOKEN = "j89Uh7HxZfGPEj3nkq9Z"
TOTAL_SPACE_GB = 3700

def get_folder_size(path):
    """Calculate total size of a folder in GB"""
    try:
        import os
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size / (1024**3)  # Convert to GB
    except Exception as e:
        print(f"Error calculating folder size: {e}")
        return 0

def main():
    print("=" * 80)
    print("PLEX SERVER STORAGE ANALYSIS")
    print("=" * 80)
    print(f"\nConnecting to Plex server: {PLEX_URL}")

    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        print(f"✓ Connected to: {plex.friendlyName}\n")

        # Get all library sections
        sections = plex.library.sections()

        library_stats = {}
        total_used_gb = 0

        print("Scanning libraries...")
        print("-" * 80)

        for section in sections:
            print(f"\nScanning: {section.title} ({section.type})")

            try:
                # Get all items in the library
                items = section.all()
                section_size = 0
                item_count = 0

                for item in items:
                    item_count += 1
                    try:
                        # Calculate size of all media files
                        if hasattr(item, 'media'):
                            for media in item.media:
                                for part in media.parts:
                                    if hasattr(part, 'size') and part.size:
                                        section_size += part.size
                    except Exception as e:
                        continue

                # Convert to GB
                section_size_gb = section_size / (1024**3)
                total_used_gb += section_size_gb

                library_stats[section.title] = {
                    'type': section.type,
                    'size_gb': section_size_gb,
                    'count': item_count
                }

                print(f"  ✓ {item_count} items, {section_size_gb:.2f} GB")

            except Exception as e:
                print(f"  ✗ Error scanning library: {e}")
                continue

        # Calculate breakdown by media type
        print("\n" + "=" * 80)
        print("STORAGE BREAKDOWN BY LIBRARY")
        print("=" * 80)
        print(f"{'Library Name':<30} {'Type':<12} {'Items':<10} {'Size (GB)':<15} {'% of Total':<10}")
        print("-" * 80)

        # Sort by size descending
        sorted_libraries = sorted(library_stats.items(), key=lambda x: x[1]['size_gb'], reverse=True)

        for lib_name, stats in sorted_libraries:
            percentage = (stats['size_gb'] / TOTAL_SPACE_GB * 100) if TOTAL_SPACE_GB > 0 else 0
            print(f"{lib_name:<30} {stats['type']:<12} {stats['count']:<10} {stats['size_gb']:<15.2f} {percentage:.1f}%")

        # Aggregate by type
        print("\n" + "=" * 80)
        print("STORAGE BREAKDOWN BY MEDIA TYPE")
        print("=" * 80)

        type_totals = {}
        for lib_name, stats in library_stats.items():
            media_type = stats['type'].capitalize() + 's'
            if media_type not in type_totals:
                type_totals[media_type] = {'size_gb': 0, 'count': 0}
            type_totals[media_type]['size_gb'] += stats['size_gb']
            type_totals[media_type]['count'] += stats['count']

        print(f"{'Media Type':<20} {'Items':<10} {'Size (GB)':<15} {'% of Total':<10}")
        print("-" * 80)

        for media_type, stats in sorted(type_totals.items(), key=lambda x: x[1]['size_gb'], reverse=True):
            percentage = (stats['size_gb'] / TOTAL_SPACE_GB * 100) if TOTAL_SPACE_GB > 0 else 0
            print(f"{media_type:<20} {stats['count']:<10} {stats['size_gb']:<15.2f} {percentage:.1f}%")

        # Overall summary
        free_space_gb = TOTAL_SPACE_GB - total_used_gb
        used_percentage = (total_used_gb / TOTAL_SPACE_GB * 100) if TOTAL_SPACE_GB > 0 else 0
        free_percentage = 100 - used_percentage

        print("\n" + "=" * 80)
        print("OVERALL STORAGE SUMMARY")
        print("=" * 80)
        print(f"Total Capacity:      {TOTAL_SPACE_GB:>10.2f} GB")
        print(f"Used Space:          {total_used_gb:>10.2f} GB  ({used_percentage:.1f}%)")
        print(f"Free Space:          {free_space_gb:>10.2f} GB  ({free_percentage:.1f}%)")
        print("=" * 80)

        # Visual bar
        bar_width = 60
        used_blocks = int((total_used_gb / TOTAL_SPACE_GB) * bar_width)
        free_blocks = bar_width - used_blocks

        print("\nStorage Visualization:")
        print("┌" + "─" * bar_width + "┐")
        print("│" + "█" * used_blocks + "░" * free_blocks + "│")
        print("└" + "─" * bar_width + "┘")
        print(f" Used: {used_percentage:.1f}%{' ' * (bar_width - 20)}Free: {free_percentage:.1f}%")

        # Warnings
        if used_percentage > 90:
            print("\n⚠️  WARNING: Storage is over 90% full!")
        elif used_percentage > 80:
            print("\n⚠️  CAUTION: Storage is over 80% full")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
