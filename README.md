# Plex Media Manager

Complete media management solution for your Plex server with web dashboard, CLI tools, and Telegram bot control.

## 🌟 Features

### Web Dashboard (NEW! 🎉)
- ✅ **Beautiful web interface** with Figma design system
- ✅ **Real-time monitoring** - Live Plex data with auto-refresh
- ✅ **Storage analytics** - Detailed breakdown by media type
- ✅ **Cleanup management** - Identify movies ready for deletion
- ✅ **Dark mode** - Toggle between light and dark themes
- ✅ **Responsive design** - Works on desktop, tablet, and mobile
- ✅ **REST API** - 5 endpoints for programmatic access

### CLI Tools
- ✅ Filters by view count (e.g., 0-1 views)
- ✅ **Time-based filtering** (not watched in last X days)
- ✅ Shows detailed list with file sizes and last watched date
- ✅ Requires double confirmation before deleting
- ✅ Dry-run mode to preview without deleting
- ✅ Supports remote Plex servers
- ✅ Deletes from both Plex and filesystem

### Telegram Bot Control
- ✅ **Remote management** via Telegram commands
- ✅ **Instant notifications** - Get summaries sent to your phone
- ✅ **Secure access** - Only authorized users can control

## Installation

```bash
cd ~/Downloads/plex-cleanup
pip install -r requirements.txt
```

---

## 🌐 Web Dashboard (NEW!)

Access your Plex Media Manager through a beautiful web interface!

### Quick Start - Web Dashboard

```bash
cd web
./start_web.sh
```

Then open: **http://localhost:8080**

![Dashboard Features](web/screenshot.png)

### Features

**Real-Time Monitoring:**
- Live statistics (movies, TV shows, storage)
- Auto-refreshes every 60 seconds
- Actual data from your Plex server

**Storage Analytics:**
- Visual breakdown by media type
- Storage charts and graphs
- Available space tracking

**Cleanup Management:**
- See movies ready for deletion
- Size and view count for each
- One-click preview

**Beautiful Design:**
- Figma design system integrated
- Dark mode with toggle
- Fully responsive (mobile, tablet, desktop)

**REST API:**
- `/api/stats` - Overall statistics
- `/api/storage` - Storage breakdown
- `/api/cleanup-candidates` - Movies to delete
- `/api/disk-usage` - Disk usage
- `/api/settings` - Configuration

### Deploy to Production

Ready to deploy to **mediamanagerdx.com**?

See the complete deployment guide: **[web/DEPLOYMENT.md](web/DEPLOYMENT.md)**

Quick deploy steps:
1. Upload files to your server
2. Install dependencies (Python, Nginx, Certbot)
3. Configure environment variables
4. Setup systemd service
5. Configure Nginx reverse proxy
6. Get SSL certificate

**Full documentation:** [web/README.md](web/README.md)

---

## 🖥️ CLI Tools

## Quick Start

### Using the Interactive Menu (Easiest)

```bash
cd ~/Downloads/plex-cleanup
./cleanup.sh
```

This will:
1. Load your configuration from `config.sh`
2. Show current settings
3. Let you choose: Preview or Delete

### Configuration

Your config is already set up in `config.sh`:
- **Server**: http://mirror.seedhost.eu:32108
- **Max Views**: 1 (movies watched 0-1 times)
- **Time Filter**: 30 days (only movies not watched in last 30 days)

To adjust settings:
```bash
nano config.sh
```

## Telegram Notifications (NEW!)

Get deletion summaries sent directly to your Telegram!

### Setup Telegram Bot

1. **Create a bot** with [@BotFather](https://t.me/BotFather):
   - Send `/newbot` to @BotFather
   - Follow prompts to name your bot
   - Save the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get your Chat ID**:
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram
   - It will reply with your Chat ID (looks like: `123456789`)

3. **Start your bot**:
   - Find your bot in Telegram (use the @username from BotFather)
   - Click "Start" or send any message to activate it

4. **Configure**:
   Edit `config.sh`:
   ```bash
   TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   TELEGRAM_CHAT_ID="123456789"
   ENABLE_TELEGRAM="yes"
   ```

Now when you run `./cleanup.sh`, summaries will be sent to your Telegram!

### What Gets Sent

- **Preview mode**: List of movies to delete (top 10) with sizes and stats
- **Delete mode**: Completion summary with number deleted and space freed

Example Telegram message:
```
🎬 PLEX CLEANUP SUMMARY

📅 Filter: Not watched in last 30 days
🎥 Total movies: 85
💾 Total size: 972.85 GB
==============================

1. Ballerina (2025)
   👁 Views: 0 | 📦 32579 MB | 📅 Never

2. Moana 2 (2024)
   👁 Views: 0 | 📦 2801 MB | 📅 2025-01-29

... and 83 more movies (937.47 GB)

==============================
TOTAL: 85 movies, 972.85 GB
```

### Remote Control via Telegram Bot (NEW!)

Control your Plex cleanup directly from Telegram with commands!

**Start the bot:**
```bash
./start_bot.sh
```

The bot will run continuously and listen for your commands. Keep it running in a terminal or use `screen`/`tmux`.

**Available Commands:**

- `/start` or `/help` - Show help and available commands
- `/status` - Show current configuration (filters, server, etc.)
- `/preview` - Scan and show movies that would be deleted
- `/delete` - Delete movies (requires confirmation: `CONFIRM DELETE`)

**Example Workflow:**
1. Send `/preview` to your bot
2. Bot replies with list of movies to delete
3. Send `/delete` to initiate deletion
4. Bot asks for confirmation
5. Reply `CONFIRM DELETE` to proceed or `CANCEL` to abort
6. Bot deletes movies and sends completion summary

**Security:**
- Only your configured Chat ID can use the bot
- Deletion requires explicit confirmation
- All commands are logged

**Running in Background:**
```bash
# Using screen
screen -S plexbot
./start_bot.sh
# Press Ctrl+A then D to detach

# To reattach
screen -r plexbot

# Or using nohup
nohup ./start_bot.sh > bot.log 2>&1 &
```

## Filtering Options

### View Count Filter
Delete movies watched X times or less:
```bash
MAX_VIEWS=1    # Delete movies with 0-1 views
MAX_VIEWS=2    # Delete movies with 0-2 views
```

### Time-Based Filter (NEW!)
Delete movies not watched in last X days:
```bash
DAYS_NOT_WATCHED=30    # Not watched in last 30 days
DAYS_NOT_WATCHED=90    # Not watched in last 90 days
DAYS_NOT_WATCHED=      # Disable (use view count only)
```

**Combined Example**: `MAX_VIEWS=1` + `DAYS_NOT_WATCHED=30` means:
- Delete movies with 0-1 views total
- **AND** not watched in the last 30 days
- This protects recently watched movies!

## Usage Examples

### Preview with 30-day filter (Recommended)
```bash
./cleanup.sh
# Choose option 1: Preview
```

### Delete movies (with confirmation)
```bash
./cleanup.sh
# Choose option 2: Delete
```

### Advanced: Direct Command
```bash
# Preview movies not watched in 30 days
python3 plex_cleanup.py \
  --url "http://mirror.seedhost.eu:32108" \
  --token "YOUR_TOKEN" \
  --max-views 1 \
  --days 30 \
  --dry-run

# With Telegram notifications
python3 plex_cleanup.py \
  --url "http://mirror.seedhost.eu:32108" \
  --token "YOUR_TOKEN" \
  --max-views 1 \
  --days 30 \
  --dry-run \
  --telegram-token "YOUR_BOT_TOKEN" \
  --telegram-chat-id "YOUR_CHAT_ID" \
  --send-telegram

# Different time periods
python3 plex_cleanup.py --url "$URL" --token "$TOKEN" --days 90 --dry-run   # 90 days
python3 plex_cleanup.py --url "$URL" --token "$TOKEN" --days 180 --dry-run  # 6 months
```

## Example Output

```
===================================================================================================================
MOVIES TO DELETE (85 movies, 972.85 GB total)
===================================================================================================================
#    Title                                         Year   Views   Size (MB)    Last Watched   Added
-------------------------------------------------------------------------------------------------------------------
1    Ballerina                                     2025   0       32579.4      Never          2025-07-01
2    Moana 2                                       2024   0       2800.6       2025-01-29     2025-09-05
3    The Holiday                                   2006   0       9964.9       Never          2025-11-25
...
-------------------------------------------------------------------------------------------------------------------
TOTAL: 85 movies, 972.85 GB
```

**Note the "Last Watched" column** - shows when each movie was last viewed!

## Current Results

With your settings (`MAX_VIEWS=1`, `DAYS_NOT_WATCHED=30`):
- **85 movies** would be deleted
- **972.85 GB** (0.97 TB) would be freed
- Movies protected: 26 movies watched in last 30 days (kept!)

## Safety Features

1. **Time-based protection**: Movies watched recently are protected
2. **Dry-run mode**: Preview before deleting
3. **Double confirmation**: Type 'DELETE' then 'YES'
4. **Detailed list**: See exactly what will be deleted
5. **Last watched date**: Know when each movie was last viewed

## Get Your Plex Token

Already configured, but to update:
1. Open Plex Web App
2. Play any movie
3. Click "..." → "Get Info" → "View XML"
4. Copy `X-Plex-Token` from URL

## Troubleshooting

### No movies found?
- Increase `DAYS_NOT_WATCHED` (e.g., 90 days instead of 30)
- Increase `MAX_VIEWS` (e.g., 2 instead of 1)

### Too many movies?
- Decrease `DAYS_NOT_WATCHED` (e.g., 14 days for very recent only)
- Decrease `MAX_VIEWS` (e.g., 0 for never watched only)

### Connection errors?
- Check Plex server URL is correct
- Verify token is valid
- Ensure Plex server is running

## What It Does

1. Connects to your Plex server
2. Scans all movie libraries
3. Finds movies matching your criteria:
   - View count ≤ MAX_VIEWS
   - Not watched in last DAYS_NOT_WATCHED days
4. Shows detailed list with last watched dates
5. Asks for double confirmation
6. Deletes from Plex and filesystem

## Warning

⚠️ **This tool PERMANENTLY deletes files!**
- Always run `--dry-run` first
- Review the list carefully
- Check "Last Watched" dates
- Files cannot be recovered after deletion

---

## 📁 Project Structure

```
plex-cleanup/
├── web/                            # Web Dashboard (NEW!)
│   ├── app.py                      # Flask web server
│   ├── index.html                  # Dashboard UI
│   ├── styles.css                  # Figma design system
│   ├── start_web.sh                # Quick start script
│   ├── .env.example                # Environment template
│   ├── plex-manager.service        # Systemd service
│   ├── nginx.conf                  # Nginx configuration
│   ├── README.md                   # Web UI documentation
│   ├── DEPLOYMENT.md               # Deployment guide
│   └── INTEGRATION_COMPLETE.md     # Integration summary
│
├── plex_cleanup.py                 # Core cleanup engine
├── storage_analyzer.py             # Storage analysis
├── disk_utils.py                   # Disk usage utilities
├── telegram_bot.py                 # Telegram bot
├── cleanup.sh                      # Interactive CLI menu
├── start_bot.sh                    # Start Telegram bot
├── config.sh                       # Configuration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🚀 Three Ways to Use Plex Media Manager

### 1. Web Dashboard (Recommended)
```bash
cd web && ./start_web.sh
# Open http://localhost:8080
```
- Beautiful UI with real-time data
- Perfect for monitoring and analysis
- Can be deployed to production server

### 2. Command Line Interface
```bash
./cleanup.sh
```
- Interactive menu system
- Perfect for scheduled tasks
- Full control over deletion process

### 3. Telegram Bot
```bash
./start_bot.sh
```
- Control from your phone
- Get instant notifications
- Remote management

---

## 🎯 Current Server Status

**Your Plex Server:**
- **URL:** http://mirror.seedhost.eu:32108
- **Storage:** 2,115 GB / 3,700 GB (57.2% used)
- **Movies:** 107 movies (1,337.69 GB)
- **TV Shows:** 33 shows (709.51 GB)
- **Training Videos:** 23 videos (67.59 GB)
- **Cleanup Ready:** 74 movies (929 GB can be freed)

**View live stats:** http://localhost:8080 (start web dashboard)

---

## 📚 Documentation

- **[web/README.md](web/README.md)** - Web dashboard user guide
- **[web/DEPLOYMENT.md](web/DEPLOYMENT.md)** - Production deployment guide
- **[web/INTEGRATION_COMPLETE.md](web/INTEGRATION_COMPLETE.md)** - Integration summary
- **[STORAGE_ANALYSIS.md](STORAGE_ANALYSIS.md)** - Storage analysis details
- **[PLEX_API_DISK_USAGE.md](PLEX_API_DISK_USAGE.md)** - Disk usage monitoring

---

## 🆕 What's New

**Latest Updates:**
- ✅ **Web Dashboard** with Figma design system
- ✅ **Live API** with auto-refreshing data
- ✅ **REST API** with 5 endpoints
- ✅ **Production deployment** configuration
- ✅ **Dark mode** with theme persistence
- ✅ **Responsive design** for all devices
- ✅ **Complete documentation** for deployment

---

## 💡 Quick Links

- **Start Web Dashboard:** `cd web && ./start_web.sh`
- **View Dashboard:** http://localhost:8080
- **API Documentation:** [web/README.md](web/README.md)
- **Deploy to Production:** [web/DEPLOYMENT.md](web/DEPLOYMENT.md)
- **Start Telegram Bot:** `./start_bot.sh`
- **CLI Menu:** `./cleanup.sh`

---

**Ready to deploy to mediamanagerdx.com? See [web/DEPLOYMENT.md](web/DEPLOYMENT.md) for complete instructions!**
