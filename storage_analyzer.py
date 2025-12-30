#!/usr/bin/env python3
"""
Storage Analyzer Module
Analyzes Plex server storage usage and generates reports
"""

import logging
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import os

try:
    from disk_utils import DiskUsage
except ImportError:
    DiskUsage = None

logger = logging.getLogger(__name__)


class StorageAnalyzer:
    """Analyze storage usage across Plex libraries"""

    def __init__(self, plex_server, total_capacity_gb: float = 3700, ssh_host: Optional[str] = None, ssh_user: Optional[str] = None):
        """
        Initialize storage analyzer

        Args:
            plex_server: PlexServer instance
            total_capacity_gb: Total storage capacity in GB
            ssh_host: SSH hostname for remote disk usage
            ssh_user: SSH username for remote disk usage
        """
        self.plex = plex_server
        self.total_capacity_gb = total_capacity_gb
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.disk_checker = DiskUsage(ssh_host, ssh_user) if DiskUsage else None

    def categorize_path(self, file_path: str, base_path: str = "/desispeed/Downloads") -> str:
        """
        Categorize file by folder structure

        Args:
            file_path: Full path to file
            base_path: Base path to strip

        Returns:
            Category name
        """
        if not file_path:
            return "Unknown"

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
            if base_path in file_path:
                relative = file_path.replace(base_path, '').strip('/')
                parts = relative.split('/')
                if parts:
                    return parts[0]
            return "Other"

    def analyze_storage(self) -> Dict:
        """
        Analyze storage usage across all libraries

        Returns:
            Dictionary with storage statistics
        """
        logger.info("Analyzing storage usage...")

        folder_stats = defaultdict(lambda: {'size_gb': 0, 'count': 0, 'paths': set()})
        library_stats = {}

        try:
            sections = self.plex.library.sections()

            for section in sections:
                logger.info(f"Scanning: {section.title}")

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

                                                category = self.categorize_path(file_path)
                                                folder_stats[category]['size_gb'] += size / (1024**3)
                                                folder_stats[category]['count'] += 1
                                                folder_stats[category]['paths'].add(os.path.dirname(file_path))

                            # For movies and music
                            elif hasattr(item, 'media'):
                                for media in item.media:
                                    for part in media.parts:
                                        if hasattr(part, 'file') and hasattr(part, 'size') and part.size:
                                            file_path = part.file
                                            size = part.size
                                            section_size += size

                                            category = self.categorize_path(file_path)
                                            folder_stats[category]['size_gb'] += size / (1024**3)
                                            folder_stats[category]['count'] += 1
                                            folder_stats[category]['paths'].add(os.path.dirname(file_path))

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

                                                    category = self.categorize_path(file_path)
                                                    folder_stats[category]['size_gb'] += size / (1024**3)
                                                    folder_stats[category]['count'] += 1
                                                    folder_stats[category]['paths'].add(os.path.dirname(file_path))

                        except Exception as e:
                            continue

                    section_size_gb = section_size / (1024**3)
                    library_stats[section.title] = {
                        'type': section.type,
                        'size_gb': section_size_gb,
                        'count': item_count
                    }

                except Exception as e:
                    logger.error(f"Error scanning {section.title}: {e}")

            # Calculate totals
            total_used_gb = sum(stats['size_gb'] for stats in folder_stats.values())
            free_gb = self.total_capacity_gb - total_used_gb

            return {
                'folder_stats': dict(folder_stats),
                'library_stats': library_stats,
                'total_used_gb': total_used_gb,
                'free_gb': free_gb,
                'used_percentage': (total_used_gb / self.total_capacity_gb * 100) if self.total_capacity_gb > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error analyzing storage: {e}")
            raise

    def get_disk_usage(self) -> Optional[Dict]:
        """
        Get actual disk usage from filesystem

        Returns:
            Disk usage dictionary or None
        """
        if not self.disk_checker:
            return None

        return self.disk_checker.get_disk_usage(prefer_remote=True, remote_path="/home32")

    def format_cli_report(self, stats: Dict) -> str:
        """
        Format storage statistics for CLI display

        Args:
            stats: Storage statistics dictionary

        Returns:
            Formatted string for CLI
        """
        lines = []

        # Add PLEX MEDIA DISK USAGE section first (from API/file scan)
        lines.append("=" * 100)
        lines.append("PLEX MEDIA DISK USAGE (from Plex API scan)")
        lines.append("=" * 100)
        lines.append(f"Total Media Files Scanned:   {sum(s['count'] for s in stats['folder_stats'].values())} files")
        lines.append(f"Total Media Size:            {stats['total_used_gb']:>10.2f} GB")
        lines.append(f"Server Capacity:             {self.total_capacity_gb:>10.2f} GB")
        lines.append(f"Media Usage:                 {stats['used_percentage']:>10.1f}%")
        lines.append(f"Available Space:             {stats['free_gb']:>10.2f} GB ({100 - stats['used_percentage']:.1f}%)")

        # Visual bar for Plex media usage
        bar_width = 80
        used_blocks = int((stats['total_used_gb'] / self.total_capacity_gb) * bar_width)
        free_blocks = bar_width - used_blocks

        lines.append("\nPlex Media Usage:")
        lines.append("┌" + "─" * bar_width + "┐")
        lines.append("│" + "█" * used_blocks + "░" * free_blocks + "│")
        lines.append("└" + "─" * bar_width + "┘")
        lines.append(f" Media: {stats['used_percentage']:.1f}%{' ' * (bar_width - 30)}Free: {100 - stats['used_percentage']:.1f}%")

        # Status indicator
        if stats['used_percentage'] > 90:
            lines.append("\n⚠️  WARNING: Media storage over 90% of capacity!")
        elif stats['used_percentage'] > 80:
            lines.append("\n⚠️  CAUTION: Media storage over 80% of capacity")
        else:
            lines.append("\n✅ Storage healthy")

        lines.append("=" * 100)
        lines.append("")

        # Add actual disk usage section if available (from filesystem)
        disk_usage = self.get_disk_usage()
        if disk_usage:
            if self.disk_checker:
                lines.append(self.disk_checker.format_disk_usage(disk_usage))
                lines.append("\n")

        lines.append("=" * 100)
        lines.append("DETAILED BREAKDOWN BY MEDIA TYPE")
        lines.append("=" * 100)
        lines.append(f"{'Category':<25} {'Files':<10} {'Size (GB)':<15} {'% of Total':<12} {'% of Used':<10}")
        lines.append("-" * 100)

        sorted_folders = sorted(stats['folder_stats'].items(), key=lambda x: x[1]['size_gb'], reverse=True)

        for category, data in sorted_folders:
            if data['size_gb'] > 0:
                pct_total = (data['size_gb'] / self.total_capacity_gb * 100) if self.total_capacity_gb > 0 else 0
                pct_used = (data['size_gb'] / stats['total_used_gb'] * 100) if stats['total_used_gb'] > 0 else 0
                lines.append(f"{category:<25} {data['count']:<10} {data['size_gb']:<15.2f} {pct_total:<12.1f} {pct_used:<10.1f}")

        # Summary
        lines.append("\n" + "=" * 100)
        lines.append("OVERALL STORAGE SUMMARY")
        lines.append("=" * 100)
        lines.append(f"Total Capacity:          {self.total_capacity_gb:>10.2f} GB  (100%)")
        lines.append(f"Used by Plex Media:      {stats['total_used_gb']:>10.2f} GB  ({stats['used_percentage']:.1f}%)")
        lines.append(f"Free / Other:            {stats['free_gb']:>10.2f} GB  ({100 - stats['used_percentage']:.1f}%)")
        lines.append("=" * 100)

        # Visual bar
        bar_width = 80
        used_blocks = int((stats['total_used_gb'] / self.total_capacity_gb) * bar_width)
        free_blocks = bar_width - used_blocks

        lines.append("\nStorage Visualization:")
        lines.append("┌" + "─" * bar_width + "┐")
        lines.append("│" + "█" * used_blocks + "░" * free_blocks + "│")
        lines.append("└" + "─" * bar_width + "┘")

        # Breakdown by category
        lines.append("\nBreakdown:")
        for category, data in sorted_folders[:5]:  # Top 5
            if data['size_gb'] > 0:
                pct = (data['size_gb'] / self.total_capacity_gb * 100)
                blocks = int((data['size_gb'] / self.total_capacity_gb) * 40)
                bar = "█" * min(blocks, 40)
                lines.append(f"  {category:<20} {bar} {data['size_gb']:>8.2f} GB ({pct:.1f}%)")

        lines.append(f"  {'Free/Other':<20} {'░' * min(free_blocks // 2, 40)} {stats['free_gb']:>8.2f} GB ({100 - stats['used_percentage']:.1f}%)")

        lines.append("\n" + "=" * 100)

        return "\n".join(lines)

    def format_telegram_report(self, stats: Dict) -> str:
        """
        Format storage statistics for Telegram

        Args:
            stats: Storage statistics dictionary

        Returns:
            Formatted HTML string for Telegram
        """
        lines = []

        # PLEX MEDIA DISK USAGE (from API scan) - Show first!
        lines.append("💾 <b>PLEX MEDIA DISK USAGE</b>\n")
        lines.append(f"📂 Scanned: {sum(s['count'] for s in stats['folder_stats'].values())} files\n")
        lines.append(f"{'=' * 30}\n\n")

        # Usage stats
        lines.append(f"<b>Total Media:</b> {stats['total_used_gb']:.1f} GB\n")
        lines.append(f"<b>Capacity:</b> {self.total_capacity_gb:.0f} GB\n")
        lines.append(f"<b>Available:</b> {stats['free_gb']:.1f} GB\n\n")

        # Progress bar for total usage
        bar_length = 20
        filled = int((stats['total_used_gb'] / self.total_capacity_gb) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        lines.append(f"<b>Media Usage: {stats['used_percentage']:.1f}%</b>\n")
        lines.append(f"{bar}\n\n")

        # Status
        if stats['used_percentage'] > 90:
            lines.append("⚠️ <b>WARNING: Over 90% full!</b>\n")
        elif stats['used_percentage'] > 80:
            lines.append("⚠️ <b>CAUTION: Over 80% full</b>\n")
        else:
            lines.append("✅ <b>Healthy</b>\n")

        lines.append(f"\n{'=' * 30}\n\n")

        # Add actual disk usage if available (from filesystem)
        disk_usage = self.get_disk_usage()
        if disk_usage and self.disk_checker:
            lines.append(self.disk_checker.format_telegram_disk_usage(disk_usage))
            lines.append(f"\n{'=' * 30}\n\n")

        lines.append("📊 <b>BREAKDOWN BY TYPE</b>\n")
        lines.append(f"{'=' * 30}\n")

        sorted_folders = sorted(stats['folder_stats'].items(), key=lambda x: x[1]['size_gb'], reverse=True)

        for category, data in sorted_folders:
            if data['size_gb'] > 0:
                pct = (data['size_gb'] / self.total_capacity_gb * 100)

                # Choose emoji based on category
                emoji = "🎬" if "Movie" in category else \
                        "📺" if "TV" in category else \
                        "🎓" if "Training" in category else \
                        "🎵" if "Music" in category else \
                        "💿" if "Software" in category else "📁"

                # Create progress bar
                bar_length = 20
                filled = int((data['size_gb'] / self.total_capacity_gb) * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)

                lines.append(f"{emoji} <b>{category}</b>")
                lines.append(f"   {bar}")
                lines.append(f"   {data['size_gb']:.1f} GB ({pct:.1f}%) • {data['count']} files\n")

        # Free space
        free_pct = 100 - stats['used_percentage']
        free_bar_filled = int((stats['free_gb'] / self.total_capacity_gb) * 20)
        free_bar = "░" * 20

        lines.append(f"✨ <b>Free Space</b>")
        lines.append(f"   {free_bar}")
        lines.append(f"   {stats['free_gb']:.1f} GB ({free_pct:.1f}%)\n")

        lines.append(f"{'=' * 30}\n")

        # Summary
        if stats['used_percentage'] > 90:
            lines.append("⚠️ <b>WARNING: Storage over 90% full!</b>")
        elif stats['used_percentage'] > 80:
            lines.append("⚠️ <b>CAUTION: Storage over 80% full</b>")
        else:
            lines.append(f"✅ <b>Storage: {stats['used_percentage']:.1f}% used</b>")

        return "".join(lines)
