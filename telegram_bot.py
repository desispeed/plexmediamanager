#!/usr/bin/env python3
"""
Telegram Bot for Plex Cleanup
Allows remote control of Plex cleanup via Telegram commands
"""

import os
import sys
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from plex_cleanup import PlexCleanup
from storage_analyzer import StorageAnalyzer
from disk_utils import DiskUsage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PLEX_URL = os.getenv('PLEX_URL')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
MAX_VIEWS = int(os.getenv('MAX_VIEWS', '1'))
DAYS_NOT_WATCHED = int(os.getenv('DAYS_NOT_WATCHED', '30')) if os.getenv('DAYS_NOT_WATCHED') else None
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
AUTHORIZED_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID'))
SSH_HOST = os.getenv('SSH_HOST', 'mirror.seedhost.eu')
SSH_USER = os.getenv('SSH_USER', 'desispeed')
REMOTE_PATH = os.getenv('REMOTE_PATH', '/home32')

# Global state for pending deletions
pending_deletion = {}


def check_authorization(func):
    """Decorator to check if user is authorized"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if chat_id != AUTHORIZED_CHAT_ID:
            await update.message.reply_text("⛔ Unauthorized. You are not allowed to use this bot.")
            logger.warning(f"Unauthorized access attempt from chat_id: {chat_id}")
            return
        return await func(update, context)
    return wrapper


@check_authorization
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🎬 <b>Plex Cleanup Bot</b>\n\n"
        "Control your Plex media cleanup remotely!\n\n"
        "Available commands:\n"
        "/preview - Show movies that would be deleted\n"
        "/select - Select movies interactively with buttons\n"
        "/delete - Delete movies (type numbers or 'all')\n"
        "/space - Analyze Plex media storage\n"
        "/disk - Check actual disk usage\n"
        "/status - Show current configuration\n"
        "/help - Show this help message",
        parse_mode='HTML'
    )


@check_authorization
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await start(update, context)


@check_authorization
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    days_text = f"{DAYS_NOT_WATCHED} days" if DAYS_NOT_WATCHED else "Disabled"

    await update.message.reply_text(
        "⚙️ <b>Current Configuration</b>\n\n"
        f"🖥 Server: {PLEX_URL}\n"
        f"👁 Max Views: {MAX_VIEWS}\n"
        f"📅 Time Filter: {days_text}\n",
        parse_mode='HTML'
    )


@check_authorization
async def analyze_space(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /space command - analyze storage usage"""
    await update.message.reply_text("💾 Analyzing storage usage...\nThis may take a moment...")

    try:
        # Initialize Plex cleanup
        cleanup = PlexCleanup(PLEX_URL, PLEX_TOKEN)

        # Analyze storage
        analyzer = StorageAnalyzer(cleanup.plex, total_capacity_gb=3700, ssh_host=SSH_HOST, ssh_user=SSH_USER)
        stats = analyzer.analyze_storage()

        # Send formatted report
        report = analyzer.format_telegram_report(stats)
        await update.message.reply_text(report, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Error in space analysis: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


@check_authorization
async def check_disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /disk command - check actual disk usage"""
    await update.message.reply_text("💾 Checking disk usage...\nThis may take a moment...")

    try:
        # Check disk usage
        disk_checker = DiskUsage(SSH_HOST, SSH_USER)
        usage = disk_checker.get_disk_usage(prefer_remote=True, remote_path=REMOTE_PATH)

        if usage:
            # Send formatted report
            report = disk_checker.format_telegram_disk_usage(usage)
            await update.message.reply_text(report, parse_mode='HTML')
        else:
            await update.message.reply_text(
                "⚠️ <b>Could not retrieve disk usage</b>\n\n"
                "SSH access may not be configured.\n"
                f"To enable: <code>ssh-copy-id {SSH_USER}@{SSH_HOST}</code>\n\n"
                "Use /space to see Plex media usage instead.",
                parse_mode='HTML'
            )

    except Exception as e:
        logger.error(f"Error checking disk usage: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


@check_authorization
async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /preview command"""
    await update.message.reply_text("🔍 Scanning your Plex library...\nThis may take a moment...")

    try:
        # Initialize Plex cleanup
        cleanup = PlexCleanup(PLEX_URL, PLEX_TOKEN)

        # Get unwatched movies
        movies = cleanup.get_unwatched_movies(
            max_view_count=MAX_VIEWS,
            days_since_watched=DAYS_NOT_WATCHED
        )

        if not movies:
            await update.message.reply_text("✅ <b>No movies found matching criteria!</b>", parse_mode='HTML')
            return

        # Format and send summary (may be multiple messages)
        messages = cleanup.format_telegram_summary(movies, DAYS_NOT_WATCHED)
        for message in messages:
            await update.message.reply_text(message, parse_mode='HTML')

        # Store for potential deletion
        pending_deletion[update.effective_chat.id] = movies
        context.user_data['selected_indices'] = set()  # Track selected movie indices

        await update.message.reply_text(
            "💡 <b>What would you like to do?</b>\n\n"
            "• <code>/delete all</code> - Delete all movies\n"
            "• <code>/delete 1,5,10</code> - Delete specific movies by number\n"
            "• <code>/select</code> - Select movies interactively with buttons",
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error in preview: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


@check_authorization
async def select_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /select command - show interactive movie selection"""
    chat_id = update.effective_chat.id

    # Check if there are pending movies
    if chat_id not in pending_deletion or not pending_deletion[chat_id]:
        await update.message.reply_text(
            "⚠️ No movies available for selection.\n\n"
            "Please run /preview first.",
            parse_mode='HTML'
        )
        return

    # Initialize selection state
    if 'selected_indices' not in context.user_data:
        context.user_data['selected_indices'] = set()
    if 'current_page' not in context.user_data:
        context.user_data['current_page'] = 0

    # Send the selection interface
    await send_selection_page(update, context, chat_id)


async def send_selection_page(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, edit_message: bool = False):
    """Send or update a page of movie selection buttons"""
    movies = pending_deletion.get(chat_id, [])
    if not movies:
        return

    page = context.user_data.get('current_page', 0)
    selected_indices = context.user_data.get('selected_indices', set())

    # Pagination settings
    MOVIES_PER_PAGE = 5
    total_pages = (len(movies) + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE
    start_idx = page * MOVIES_PER_PAGE
    end_idx = min(start_idx + MOVIES_PER_PAGE, len(movies))

    # Build message with movie list
    message = f"🎬 <b>Select Movies to Delete</b>\n"
    message += f"Page {page + 1}/{total_pages} | Selected: {len(selected_indices)}/{len(movies)}\n\n"

    # Build keyboard with movie buttons
    keyboard = []
    for idx in range(start_idx, end_idx):
        movie = movies[idx]
        is_selected = idx in selected_indices
        checkbox = "✅" if is_selected else "⬜"
        title = movie['title'][:30] + '...' if len(movie['title']) > 30 else movie['title']
        size_gb = movie['file_size_mb'] / 1024

        button_text = f"{checkbox} {idx + 1}. {title} ({size_gb:.1f}GB)"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"toggle_{idx}")])

    # Add navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data="page_prev"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data="page_next"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    # Add action buttons
    action_buttons = [
        InlineKeyboardButton("Select All", callback_data="select_all"),
        InlineKeyboardButton("Clear All", callback_data="clear_all")
    ]
    keyboard.append(action_buttons)

    # Add done/cancel buttons
    if len(selected_indices) > 0:
        keyboard.append([InlineKeyboardButton("✅ Done - Confirm Selection", callback_data="done_selection")])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_selection")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send or edit message
    try:
        if edit_message and update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error sending selection page: {e}")


async def handle_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks for movie selection"""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    movies = pending_deletion.get(chat_id, [])

    if not movies:
        await query.edit_message_text("❌ No movies available.")
        return

    data = query.data
    selected_indices = context.user_data.get('selected_indices', set())

    # Handle toggle individual movie
    if data.startswith("toggle_"):
        idx = int(data.split("_")[1])
        if idx in selected_indices:
            selected_indices.remove(idx)
        else:
            selected_indices.add(idx)
        context.user_data['selected_indices'] = selected_indices
        await send_selection_page(update, context, chat_id, edit_message=True)

    # Handle page navigation
    elif data == "page_prev":
        context.user_data['current_page'] = max(0, context.user_data.get('current_page', 0) - 1)
        await send_selection_page(update, context, chat_id, edit_message=True)

    elif data == "page_next":
        context.user_data['current_page'] = context.user_data.get('current_page', 0) + 1
        await send_selection_page(update, context, chat_id, edit_message=True)

    # Handle select/clear all
    elif data == "select_all":
        context.user_data['selected_indices'] = set(range(len(movies)))
        await send_selection_page(update, context, chat_id, edit_message=True)

    elif data == "clear_all":
        context.user_data['selected_indices'] = set()
        await send_selection_page(update, context, chat_id, edit_message=True)

    # Handle done selection
    elif data == "done_selection":
        selected_indices = context.user_data.get('selected_indices', set())
        if not selected_indices:
            await query.answer("⚠️ No movies selected!", show_alert=True)
            return

        selected_movies = [movies[i] for i in sorted(selected_indices)]
        context.user_data['selected_movies'] = selected_movies

        total_size_gb = sum(m['file_size_mb'] for m in selected_movies) / 1024

        # Show confirmation
        summary = f"⚠️ <b>DELETION CONFIRMATION REQUIRED</b>\n\n"
        summary += f"Selected movies to delete:\n"
        summary += f"🎥 {len(selected_movies)} movies\n"
        summary += f"💾 {total_size_gb:.2f} GB\n\n"

        # Show first 5 selected movies
        for movie in selected_movies[:5]:
            title = movie['title'][:30] + '...' if len(movie['title']) > 30 else movie['title']
            summary += f"• {title} ({movie['year']}) - {movie['file_size_mb']:.0f} MB\n"

        if len(selected_movies) > 5:
            summary += f"... and {len(selected_movies) - 5} more\n"

        summary += f"\n<b>To confirm, reply with:</b> <code>CONFIRM DELETE</code>\n"
        summary += f"<b>To cancel, reply with:</b> <code>CANCEL</code>"

        await query.edit_message_text(summary, parse_mode='HTML')
        context.user_data['awaiting_confirmation'] = True

    # Handle cancel
    elif data == "cancel_selection":
        context.user_data['selected_indices'] = set()
        context.user_data['current_page'] = 0
        await query.edit_message_text("✅ Selection cancelled.")


def parse_movie_selection(selection: str, total_movies: int) -> List[int]:
    """
    Parse movie selection string and return list of movie indices

    Args:
        selection: Selection string (e.g., "all", "1,5,10", "1-20", "1-10,25,30-40")
        total_movies: Total number of movies available

    Returns:
        List of movie indices (0-based)
    """
    if selection.lower() == "all":
        return list(range(total_movies))

    indices = set()
    parts = selection.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            # Handle range (e.g., "1-20")
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                # Validate range
                if start < 1 or end > total_movies or start > end:
                    raise ValueError(f"Invalid range: {part}")
                # Add all numbers in range (convert to 0-based index)
                indices.update(range(start - 1, end))
            except ValueError as e:
                raise ValueError(f"Invalid range format: {part}")
        else:
            # Handle single number
            try:
                num = int(part.strip())
                if num < 1 or num > total_movies:
                    raise ValueError(f"Number {num} out of range (1-{total_movies})")
                indices.add(num - 1)  # Convert to 0-based index
            except ValueError:
                raise ValueError(f"Invalid number: {part}")

    return sorted(list(indices))


@check_authorization
async def delete_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /delete command with optional selection"""
    chat_id = update.effective_chat.id

    # Check if there are pending movies to delete
    if chat_id not in pending_deletion or not pending_deletion[chat_id]:
        await update.message.reply_text(
            "⚠️ No movies queued for deletion.\n\n"
            "Please run /preview first to see what would be deleted.",
            parse_mode='HTML'
        )
        return

    all_movies = pending_deletion[chat_id]

    # Parse selection from command arguments
    selection = " ".join(context.args) if context.args else "all"

    try:
        # Parse the selection
        selected_indices = parse_movie_selection(selection, len(all_movies))
        selected_movies = [all_movies[i] for i in selected_indices]

        # Store selected movies for confirmation
        context.user_data['selected_movies'] = selected_movies

        total_size_gb = sum(m['file_size_mb'] for m in selected_movies) / 1024

        # Show selected movies summary
        summary = f"⚠️ <b>DELETION CONFIRMATION REQUIRED</b>\n\n"
        summary += f"Selected movies to delete:\n"
        summary += f"🎥 {len(selected_movies)} movies\n"
        summary += f"💾 {total_size_gb:.2f} GB\n\n"

        # Show first 5 selected movies
        if len(selected_movies) <= 5:
            for movie in selected_movies:
                title = movie['title'][:30] + '...' if len(movie['title']) > 30 else movie['title']
                summary += f"• {title} ({movie['year']}) - {movie['file_size_mb']:.0f} MB\n"
        else:
            for movie in selected_movies[:5]:
                title = movie['title'][:30] + '...' if len(movie['title']) > 30 else movie['title']
                summary += f"• {title} ({movie['year']}) - {movie['file_size_mb']:.0f} MB\n"
            summary += f"... and {len(selected_movies) - 5} more\n"

        summary += f"\n<b>To confirm, reply with:</b> <code>CONFIRM DELETE</code>\n"
        summary += f"<b>To cancel, reply with:</b> <code>CANCEL</code>"

        await update.message.reply_text(summary, parse_mode='HTML')

        # Set a flag to wait for confirmation
        context.user_data['awaiting_confirmation'] = True

    except ValueError as e:
        await update.message.reply_text(
            f"❌ <b>Invalid selection:</b> {str(e)}\n\n"
            f"Examples:\n"
            f"• /delete all\n"
            f"• /delete 1,5,10\n"
            f"• /delete 1-20\n"
            f"• /delete 1-10,25,30-40",
            parse_mode='HTML'
        )


@check_authorization
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (for confirmation)"""
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    # Check if we're waiting for confirmation
    if context.user_data.get('awaiting_confirmation'):
        if text == "CONFIRM DELETE":
            context.user_data['awaiting_confirmation'] = False
            await execute_deletion(update, context)
        elif text == "CANCEL":
            context.user_data['awaiting_confirmation'] = False
            context.user_data.pop('selected_movies', None)
            await update.message.reply_text("✅ Deletion cancelled.")
        else:
            await update.message.reply_text(
                "⚠️ Please reply with either:\n"
                "<code>CONFIRM DELETE</code> or <code>CANCEL</code>",
                parse_mode='HTML'
            )
    else:
        await update.message.reply_text(
            "👋 Use /help to see available commands."
        )


async def execute_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute the actual deletion"""
    chat_id = update.effective_chat.id

    # Get selected movies from user_data (or all pending if not specified)
    movies = context.user_data.get('selected_movies')

    if not movies:
        await update.message.reply_text("❌ No movies to delete.")
        return
    await update.message.reply_text(
        f"🗑 <b>Starting deletion of {len(movies)} movies...</b>\n"
        f"This may take a few minutes.",
        parse_mode='HTML'
    )

    try:
        # Initialize Plex cleanup
        cleanup = PlexCleanup(PLEX_URL, PLEX_TOKEN)

        deleted_count = 0
        failed_count = 0

        # Delete movies one by one
        for idx, movie in enumerate(movies, 1):
            try:
                movie['plex_object'].delete()
                deleted_count += 1

                # Send progress update every 10 movies
                if idx % 10 == 0:
                    await update.message.reply_text(
                        f"⏳ Progress: {idx}/{len(movies)} movies processed..."
                    )

            except Exception as e:
                logger.error(f"Failed to delete {movie['title']}: {e}")
                failed_count += 1

        # Calculate freed space
        deleted_size_gb = sum(m['file_size_mb'] for m in movies[:deleted_count]) / 1024

        # Send completion message
        completion_msg = f"✅ <b>DELETION COMPLETED</b>\n\n"
        completion_msg += f"✓ Successfully deleted: {deleted_count} movies\n"
        completion_msg += f"💾 Space freed: {deleted_size_gb:.2f} GB\n"
        if failed_count > 0:
            completion_msg += f"❌ Failed: {failed_count} movies\n"

        await update.message.reply_text(completion_msg, parse_mode='HTML')

        # Clear pending deletion and selected movies
        pending_deletion.pop(chat_id, None)
        context.user_data.pop('selected_movies', None)

    except Exception as e:
        logger.error(f"Error during deletion: {e}")
        await update.message.reply_text(f"❌ Error during deletion: {str(e)}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again or contact the administrator."
        )


async def main_async():
    """Async main function"""
    if not all([PLEX_URL, PLEX_TOKEN, TELEGRAM_BOT_TOKEN, AUTHORIZED_CHAT_ID]):
        logger.error("Missing required environment variables!")
        logger.error("Required: PLEX_URL, PLEX_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")
        sys.exit(1)

    logger.info("Starting Plex Cleanup Telegram Bot...")
    logger.info(f"Authorized Chat ID: {AUTHORIZED_CHAT_ID}")

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("space", analyze_space))
    application.add_handler(CommandHandler("disk", check_disk))
    application.add_handler(CommandHandler("preview", preview))
    application.add_handler(CommandHandler("select", select_movies))
    application.add_handler(CommandHandler("delete", delete_movies))

    # Add callback query handler for button clicks
    application.add_handler(CallbackQueryHandler(handle_selection_callback))

    # Add message handler for confirmations
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("✓ Bot started! Send /start to begin.")

    # Initialize and start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # Keep the bot running
    try:
        # Run until interrupted
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


def main():
    """Start the bot"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
