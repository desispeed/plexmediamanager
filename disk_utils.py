#!/usr/bin/env python3
"""
Disk Usage Utilities
Get disk usage information from local or remote systems
"""

import subprocess
import shutil
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DiskUsage:
    """Get disk usage information"""

    def __init__(self, ssh_host: Optional[str] = None, ssh_user: Optional[str] = None):
        """
        Initialize disk usage checker

        Args:
            ssh_host: SSH hostname (e.g., 'mirror.seedhost.eu')
            ssh_user: SSH username (e.g., 'desispeed')
        """
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user

    def get_local_disk_usage(self, path: str = "/") -> Dict:
        """
        Get disk usage for local filesystem

        Args:
            path: Path to check (default: root)

        Returns:
            Dictionary with total, used, free, and percent
        """
        try:
            usage = shutil.disk_usage(path)
            return {
                'total_gb': usage.total / (1024**3),
                'used_gb': usage.used / (1024**3),
                'free_gb': usage.free / (1024**3),
                'percent': (usage.used / usage.total * 100) if usage.total > 0 else 0,
                'path': path,
                'source': 'local'
            }
        except Exception as e:
            logger.error(f"Error getting local disk usage: {e}")
            return None

    def get_remote_disk_usage(self, remote_path: str = "/home32") -> Dict:
        """
        Get disk usage from remote server via SSH

        Args:
            remote_path: Remote path to check

        Returns:
            Dictionary with disk usage info or None if SSH not available
        """
        if not self.ssh_host:
            logger.warning("No SSH host configured")
            return None

        ssh_target = f"{self.ssh_user}@{self.ssh_host}" if self.ssh_user else self.ssh_host

        try:
            # Check if SSH is available and key-based auth is set up
            test_cmd = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5', ssh_target, 'echo ok']
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                logger.info("SSH key-based authentication not set up")
                return None

            # Get disk usage via df command
            cmd = ['ssh', ssh_target, f'df -B1 {remote_path}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                # Parse df output
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    # Second line has the data
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        total_bytes = int(parts[1])
                        used_bytes = int(parts[2])
                        free_bytes = int(parts[3])
                        percent_str = parts[4].rstrip('%')

                        return {
                            'total_gb': total_bytes / (1024**3),
                            'used_gb': used_bytes / (1024**3),
                            'free_gb': free_bytes / (1024**3),
                            'percent': float(percent_str) if percent_str else 0,
                            'path': remote_path,
                            'source': 'remote',
                            'host': self.ssh_host
                        }

            return None

        except subprocess.TimeoutExpired:
            logger.error("SSH command timed out")
            return None
        except Exception as e:
            logger.error(f"Error getting remote disk usage: {e}")
            return None

    def get_disk_usage(self, prefer_remote: bool = True, remote_path: str = "/home32") -> Dict:
        """
        Get disk usage, trying remote first if configured, then falling back to local

        Args:
            prefer_remote: Try remote SSH first if configured
            remote_path: Remote path to check

        Returns:
            Dictionary with disk usage info
        """
        if prefer_remote and self.ssh_host:
            logger.info(f"Attempting to get disk usage from {self.ssh_host}:{remote_path}")
            remote_usage = self.get_remote_disk_usage(remote_path)
            if remote_usage:
                logger.info("✓ Got disk usage from remote server")
                return remote_usage
            else:
                logger.info("Could not get remote disk usage, using estimated values")

        # If remote fails or not configured, return None to indicate we should use estimates
        logger.info("Using Plex media size as estimate (actual disk usage may differ)")
        return None

    def format_disk_usage(self, usage: Dict) -> str:
        """
        Format disk usage info as a string

        Args:
            usage: Disk usage dictionary

        Returns:
            Formatted string
        """
        if not usage:
            return "Disk usage information not available"

        lines = []
        lines.append("=" * 80)
        lines.append("DISK USAGE INFORMATION")
        lines.append("=" * 80)

        if usage.get('source') == 'remote':
            lines.append(f"Source: Remote server ({usage.get('host')})")
            lines.append(f"Path: {usage.get('path')}")
        else:
            lines.append(f"Source: Local filesystem")
            lines.append(f"Path: {usage.get('path')}")

        lines.append("")
        lines.append(f"Total Capacity:   {usage['total_gb']:>10.2f} GB")
        lines.append(f"Used Space:       {usage['used_gb']:>10.2f} GB  ({usage['percent']:.1f}%)")
        lines.append(f"Free Space:       {usage['free_gb']:>10.2f} GB  ({100 - usage['percent']:.1f}%)")

        # Visual bar
        bar_width = 60
        used_blocks = int((usage['percent'] / 100) * bar_width)
        free_blocks = bar_width - used_blocks

        lines.append("")
        lines.append("Disk Usage:")
        lines.append("┌" + "─" * bar_width + "┐")
        lines.append("│" + "█" * used_blocks + "░" * free_blocks + "│")
        lines.append("└" + "─" * bar_width + "┘")
        lines.append(f" Used: {usage['percent']:.1f}%{' ' * (bar_width - 30)}Free: {100 - usage['percent']:.1f}%")

        # Warnings
        if usage['percent'] > 90:
            lines.append("\n⚠️  WARNING: Disk is over 90% full!")
        elif usage['percent'] > 80:
            lines.append("\n⚠️  CAUTION: Disk is over 80% full")

        lines.append("=" * 80)

        return "\n".join(lines)

    def format_telegram_disk_usage(self, usage: Dict) -> str:
        """
        Format disk usage for Telegram

        Args:
            usage: Disk usage dictionary

        Returns:
            Formatted HTML string
        """
        if not usage:
            return "💾 <b>Disk Usage</b>\n\n❌ Information not available\n"

        lines = []
        lines.append("💾 <b>DISK USAGE</b>\n")

        if usage.get('source') == 'remote':
            lines.append(f"📡 Remote: {usage.get('host')}\n")
        else:
            lines.append(f"💻 Local: {usage.get('path')}\n")

        lines.append(f"{'=' * 30}\n")

        # Progress bar
        bar_length = 20
        filled = int((usage['percent'] / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        lines.append(f"<b>Capacity:</b> {usage['total_gb']:.0f} GB\n")
        lines.append(f"{bar}\n")
        lines.append(f"<b>Used:</b> {usage['used_gb']:.1f} GB ({usage['percent']:.1f}%)\n")
        lines.append(f"<b>Free:</b> {usage['free_gb']:.1f} GB ({100 - usage['percent']:.1f}%)\n")

        # Status emoji
        if usage['percent'] > 90:
            lines.append("\n⚠️ <b>WARNING: Over 90% full!</b>")
        elif usage['percent'] > 80:
            lines.append("\n⚠️ <b>CAUTION: Over 80% full</b>")
        elif usage['percent'] > 70:
            lines.append("\n⚡ <b>Getting full</b>")
        else:
            lines.append("\n✅ <b>Healthy</b>")

        return "".join(lines)
