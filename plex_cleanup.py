#!/usr/bin/env python3
"""
Plex Media Cleanup Tool
Finds and deletes movies that have been watched once or less
"""

import argparse
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import sys
import asyncio

try:
    from plexapi.server import PlexServer
    from plexapi.video import Movie
except ImportError:
    print("Error: plexapi library not installed")
    print("Install with: pip install plexapi")
    sys.exit(1)

try:
    from storage_analyzer import StorageAnalyzer
except ImportError:
    print("Warning: storage_analyzer module not found")
    StorageAnalyzer = None

try:
    from disk_utils import DiskUsage
except ImportError:
    DiskUsage = None

try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot not installed. Telegram notifications disabled.")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PlexCleanup:
    """
    Plex media cleanup utility
    """

    def __init__(self, plex_url: str, plex_token: str, telegram_bot_token: str = None, telegram_chat_id: str = None):
        """
        Initialize Plex cleanup tool

        Args:
            plex_url: Plex server URL (e.g., http://192.168.1.100:32400)
            plex_token: Plex authentication token
            telegram_bot_token: Telegram bot token (optional)
            telegram_chat_id: Telegram chat ID (optional)
        """
        try:
            logger.info(f"Connecting to Plex server at {plex_url}")
            self.plex = PlexServer(plex_url, plex_token)
            logger.info(f"✓ Connected to Plex server: {self.plex.friendlyName}")
        except Exception as e:
            logger.error(f"Failed to connect to Plex: {e}")
            raise

        # Initialize Telegram bot if credentials provided
        self.telegram_bot = None
        self.telegram_chat_id = telegram_chat_id
        if telegram_bot_token and telegram_chat_id and TELEGRAM_AVAILABLE:
            try:
                self.telegram_bot = Bot(token=telegram_bot_token)
                logger.info("✓ Telegram bot initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Telegram bot: {e}")

    async def send_telegram_message(self, message: str):
        """
        Send a message to Telegram

        Args:
            message: Message text to send
        """
        if not self.telegram_bot or not self.telegram_chat_id:
            logger.warning("Telegram not configured, skipping notification")
            return False

        try:
            await self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info("✓ Telegram message sent successfully")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def format_telegram_summary(self, movies: List[Dict], days_filter: int = None, max_movies: int = None) -> List[str]:
        """
        Format movie list as Telegram messages (may return multiple messages if needed)

        Args:
            movies: List of movie dictionaries
            days_filter: Number of days used for filtering
            max_movies: Maximum number of movies to show (None = all)

        Returns:
            List of formatted message strings
        """
        if not movies:
            return ["✅ <b>No movies found matching criteria!</b>"]

        total_size_gb = sum(m['file_size_mb'] for m in movies) / 1024

        header = f"🎬 <b>PLEX CLEANUP SUMMARY</b>\n\n"
        if days_filter:
            header += f"📅 Filter: Not watched in last {days_filter} days\n"
        header += f"🎥 Total movies: {len(movies)}\n"
        header += f"💾 Total size: {total_size_gb:.2f} GB\n"
        header += f"{'=' * 30}\n\n"

        messages = []
        current_message = header
        movies_to_show = movies if max_movies is None else movies[:max_movies]

        for idx, movie in enumerate(movies_to_show, 1):
            title = movie['title'][:35] + '...' if len(movie['title']) > 35 else movie['title']
            size_mb = movie['file_size_mb']
            views = movie['view_count']
            last_watched = movie['last_viewed']

            movie_text = f"{idx}. <b>{title}</b> ({movie['year']})\n"
            movie_text += f"   👁 Views: {views} | 📦 {size_mb:.0f} MB | 📅 {last_watched}\n\n"

            # Check if adding this movie would exceed Telegram's limit (4096 chars)
            if len(current_message + movie_text) > 3800:  # Leave some buffer
                # Finalize current message and start new one
                messages.append(current_message)
                current_message = f"🎬 <b>CONTINUED...</b>\n\n" + movie_text
            else:
                current_message += movie_text

        # Add footer to last message
        footer = f"{'=' * 30}\n"
        footer += f"<b>TOTAL: {len(movies)} movies, {total_size_gb:.2f} GB</b>"

        if len(current_message + footer) > 4000:
            messages.append(current_message)
            messages.append(footer)
        else:
            current_message += footer
            messages.append(current_message)

        return messages

    def get_unwatched_movies(self, max_view_count: int = 1, days_since_watched: int = None) -> List[Dict]:
        """
        Get movies that have been watched max_view_count times or less
        Optionally filter by last watched date

        Args:
            max_view_count: Maximum view count (default: 1)
            days_since_watched: Only include movies not watched in last X days (optional)

        Returns:
            List of movie dictionaries with details
        """
        unwatched_movies = []
        cutoff_date = None

        if days_since_watched:
            cutoff_date = datetime.now() - timedelta(days=days_since_watched)
            logger.info(f"Filtering for movies not watched since {cutoff_date.strftime('%Y-%m-%d')}")

        try:
            # Get all movie libraries
            movie_sections = [s for s in self.plex.library.sections() if s.type == 'movie']

            if not movie_sections:
                logger.warning("No movie libraries found in Plex")
                return []

            logger.info(f"Found {len(movie_sections)} movie library/libraries")

            for section in movie_sections:
                logger.info(f"Scanning library: {section.title}")
                movies = section.all()

                for movie in movies:
                    view_count = movie.viewCount if movie.viewCount else 0

                    # Check view count first
                    if view_count > max_view_count:
                        continue

                    # If time-based filtering is enabled
                    if cutoff_date:
                        last_viewed = movie.lastViewedAt if hasattr(movie, 'lastViewedAt') and movie.lastViewedAt else None

                        # If never watched, include it
                        if last_viewed is None:
                            pass  # Include it
                        # If watched recently (within cutoff period), skip it
                        elif last_viewed > cutoff_date:
                            continue
                        # If watched but before cutoff date, include it

                    # Get file info
                    file_paths = [media.parts[0].file for media in movie.media]
                    file_size = sum(media.parts[0].size for media in movie.media)

                    last_viewed_str = 'Never'
                    if hasattr(movie, 'lastViewedAt') and movie.lastViewedAt:
                        last_viewed_str = movie.lastViewedAt.strftime('%Y-%m-%d')

                    unwatched_movies.append({
                        'title': movie.title,
                        'year': movie.year,
                        'view_count': view_count,
                        'added_date': movie.addedAt.strftime('%Y-%m-%d') if movie.addedAt else 'Unknown',
                        'last_viewed': last_viewed_str,
                        'file_paths': file_paths,
                        'file_size_mb': file_size / (1024 * 1024),
                        'rating': movie.rating if hasattr(movie, 'rating') else None,
                        'plex_object': movie
                    })

            # Sort by view count, then by added date (oldest first)
            unwatched_movies.sort(key=lambda x: (x['view_count'], x['added_date']))

            if days_since_watched:
                logger.info(f"Found {len(unwatched_movies)} movies with {max_view_count} view(s) or less, not watched in {days_since_watched} days")
            else:
                logger.info(f"Found {len(unwatched_movies)} movies with {max_view_count} view(s) or less")

        except Exception as e:
            logger.error(f"Error scanning movies: {e}")
            raise

        return unwatched_movies

    def print_movie_list(self, movies: List[Dict]):
        """
        Print formatted list of movies

        Args:
            movies: List of movie dictionaries
        """
        if not movies:
            print("\n✓ No movies found matching criteria!")
            return

        total_size_gb = sum(m['file_size_mb'] for m in movies) / 1024

        print("\n" + "=" * 115)
        print(f"MOVIES TO DELETE ({len(movies)} movies, {total_size_gb:.2f} GB total)")
        print("=" * 115)
        print(f"{'#':<4} {'Title':<45} {'Year':<6} {'Views':<7} {'Size (MB)':<12} {'Last Watched':<14} {'Added':<12}")
        print("-" * 115)

        for idx, movie in enumerate(movies, 1):
            title = movie['title'][:42] + '...' if len(movie['title']) > 45 else movie['title']
            print(f"{idx:<4} {title:<45} {movie['year'] or 'N/A':<6} "
                  f"{movie['view_count']:<7} {movie['file_size_mb']:<12.1f} {movie['last_viewed']:<14} {movie['added_date']:<12}")

        print("-" * 115)
        print(f"TOTAL: {len(movies)} movies, {total_size_gb:.2f} GB\n")

    def delete_movies(self, movies: List[Dict], dry_run: bool = False, days_filter: int = None, send_telegram: bool = False):
        """
        Delete movies from Plex and filesystem

        Args:
            movies: List of movie dictionaries to delete
            dry_run: If True, only preview without deleting
            days_filter: Number of days used for filtering (for display purposes)
            send_telegram: If True, send summary to Telegram
        """
        if not movies:
            logger.info("No movies to delete")
            if send_telegram:
                asyncio.run(self.send_telegram_message("✅ <b>No movies found matching criteria!</b>"))
            return

        if dry_run:
            if days_filter:
                logger.info(f"DRY RUN MODE - Showing movies not watched in last {days_filter} days")
            else:
                logger.info("DRY RUN MODE - No files will be deleted")
            self.print_movie_list(movies)

            # Send Telegram notification if requested
            if send_telegram:
                messages = self.format_telegram_summary(movies, days_filter)
                for message in messages:
                    asyncio.run(self.send_telegram_message(message))

            return

        # Show list and ask for confirmation
        self.print_movie_list(movies)

        print("\n⚠️  WARNING: This will PERMANENTLY delete these movies from your Plex server and filesystem!")
        confirmation = input("\nType 'DELETE' to confirm deletion (anything else to cancel): ")

        if confirmation != 'DELETE':
            logger.info("Deletion cancelled by user")
            return

        # Second confirmation for safety
        print(f"\n⚠️  FINAL CONFIRMATION: Delete {len(movies)} movies?")
        final_confirm = input("Type 'YES' to proceed: ")

        if final_confirm != 'YES':
            logger.info("Deletion cancelled by user")
            return

        logger.info(f"Starting deletion of {len(movies)} movies...")
        deleted_count = 0
        failed_count = 0

        for idx, movie in enumerate(movies, 1):
            try:
                logger.info(f"[{idx}/{len(movies)}] Deleting: {movie['title']} ({movie['year']})")

                # Delete from Plex (this also deletes the file if configured)
                movie['plex_object'].delete()
                deleted_count += 1

                logger.info(f"  ✓ Deleted successfully")

            except Exception as e:
                logger.error(f"  ✗ Failed to delete: {e}")
                failed_count += 1

        print("\n" + "=" * 60)
        print(f"DELETION COMPLETE")
        print(f"✓ Successfully deleted: {deleted_count} movies")
        if failed_count > 0:
            print(f"✗ Failed to delete: {failed_count} movies")
        print("=" * 60)

        # Send Telegram notification if requested
        if send_telegram:
            deleted_size_gb = sum(m['file_size_mb'] for m in movies[:deleted_count]) / 1024
            completion_msg = f"🗑 <b>DELETION COMPLETED</b>\n\n"
            completion_msg += f"✅ Successfully deleted: {deleted_count} movies\n"
            completion_msg += f"💾 Space freed: {deleted_size_gb:.2f} GB\n"
            if failed_count > 0:
                completion_msg += f"❌ Failed: {failed_count} movies\n"
            asyncio.run(self.send_telegram_message(completion_msg))

    def analyze_storage(self, send_telegram: bool = False, total_capacity_gb: float = 3700, ssh_host: str = None, ssh_user: str = None):
        """
        Analyze and display storage usage across Plex libraries

        Args:
            send_telegram: If True, send report to Telegram
            total_capacity_gb: Total storage capacity in GB
            ssh_host: SSH hostname for remote disk usage
            ssh_user: SSH username for remote disk usage
        """
        if not StorageAnalyzer:
            logger.error("StorageAnalyzer module not available")
            return

        try:
            analyzer = StorageAnalyzer(self.plex, total_capacity_gb, ssh_host, ssh_user)
            stats = analyzer.analyze_storage()

            # Print CLI report
            report = analyzer.format_cli_report(stats)
            print(report)

            # Send Telegram notification if requested
            if send_telegram:
                telegram_report = analyzer.format_telegram_report(stats)
                asyncio.run(self.send_telegram_message(telegram_report))

        except Exception as e:
            logger.error(f"Error analyzing storage: {e}")
            raise

    def check_disk_usage(self, send_telegram: bool = False, ssh_host: str = None, ssh_user: str = None, remote_path: str = "/home32"):
        """
        Check actual disk usage on the server

        Args:
            send_telegram: If True, send report to Telegram
            ssh_host: SSH hostname
            ssh_user: SSH username
            remote_path: Remote path to check
        """
        if not DiskUsage:
            logger.error("DiskUsage module not available")
            return

        try:
            disk_checker = DiskUsage(ssh_host, ssh_user)
            usage = disk_checker.get_disk_usage(prefer_remote=True, remote_path=remote_path)

            if usage:
                # Print CLI report
                report = disk_checker.format_disk_usage(usage)
                print(report)

                # Send Telegram notification if requested
                if send_telegram:
                    telegram_report = disk_checker.format_telegram_disk_usage(usage)
                    asyncio.run(self.send_telegram_message(telegram_report))
            else:
                logger.warning("Could not retrieve disk usage. SSH may not be configured.")
                print("\n⚠️  Could not retrieve actual disk usage.")
                print("To enable disk usage monitoring:")
                print("  1. Set up SSH key authentication to your server")
                print(f"  2. Run: ssh-copy-id {ssh_user}@{ssh_host}" if ssh_user and ssh_host else "")
                print("\nFor now, use --analyze-storage to see Plex media usage.\n")

        except Exception as e:
            logger.error(f"Error checking disk usage: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description="Plex Movie Cleanup Tool")
    parser.add_argument("--url", required=True, help="Plex server URL (e.g., http://192.168.1.100:32400)")
    parser.add_argument("--token", required=True, help="Plex authentication token")
    parser.add_argument("--max-views", type=int, default=1, help="Maximum view count (default: 1)")
    parser.add_argument("--days", type=int, help="Only include movies not watched in last X days")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't delete")
    parser.add_argument("--auto-delete", action="store_true", help="Skip confirmation (use with caution!)")
    parser.add_argument("--analyze-storage", action="store_true", help="Analyze storage usage across libraries")
    parser.add_argument("--check-disk", action="store_true", help="Check actual disk usage on server")
    parser.add_argument("--total-capacity", type=float, default=3700, help="Total storage capacity in GB (default: 3700)")
    parser.add_argument("--ssh-host", help="SSH hostname for remote disk usage (e.g., mirror.seedhost.eu)")
    parser.add_argument("--ssh-user", help="SSH username (e.g., desispeed)")
    parser.add_argument("--remote-path", default="/home32", help="Remote path to check disk usage (default: /home32)")
    parser.add_argument("--telegram-token", help="Telegram bot token")
    parser.add_argument("--telegram-chat-id", help="Telegram chat ID")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary to Telegram")

    args = parser.parse_args()

    try:
        # Initialize cleanup tool
        cleanup = PlexCleanup(
            args.url,
            args.token,
            telegram_bot_token=args.telegram_token,
            telegram_chat_id=args.telegram_chat_id
        )

        # If checking disk usage, do that and exit
        if args.check_disk:
            cleanup.check_disk_usage(
                send_telegram=args.send_telegram,
                ssh_host=args.ssh_host,
                ssh_user=args.ssh_user,
                remote_path=args.remote_path
            )
            return

        # If analyzing storage, do that and exit
        if args.analyze_storage:
            cleanup.analyze_storage(
                send_telegram=args.send_telegram,
                total_capacity_gb=args.total_capacity,
                ssh_host=args.ssh_host,
                ssh_user=args.ssh_user
            )
            return

        # Get unwatched movies
        unwatched = cleanup.get_unwatched_movies(
            max_view_count=args.max_views,
            days_since_watched=args.days
        )

        if args.dry_run:
            cleanup.delete_movies(
                unwatched,
                dry_run=True,
                days_filter=args.days,
                send_telegram=args.send_telegram
            )
        else:
            cleanup.delete_movies(
                unwatched,
                dry_run=False,
                days_filter=args.days,
                send_telegram=args.send_telegram
            )

    except KeyboardInterrupt:
        logger.info("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
