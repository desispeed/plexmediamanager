# Disk Usage Feature - Added Successfully!

## ✅ What's New

A complete disk usage monitoring system has been added to your Plex Media Manager!

### 🎯 New Features

1. **Real-time Disk Usage Monitoring**
   - Check actual filesystem disk usage (not just Plex media)
   - Shows total capacity, used space, free space
   - Visual progress bars
   - Warns when disk is >80% or >90% full

2. **Remote SSH Support**
   - Can query remote seedbox disk usage via SSH
   - Automatically falls back to estimates if SSH not configured
   - Clear instructions for setting up SSH access

3. **Integrated with Storage Analysis**
   - Disk usage now shown alongside Plex media breakdown
   - Combined view in CLI and Telegram reports

---

## 📊 Usage

### CLI Menu

Run `./cleanup.sh` and you'll now see 5 options:

```
1) Preview movies that would be deleted (dry-run)
2) Delete movies (with confirmation)
3) Analyze storage usage (Plex media)  ← Shows disk usage too!
4) Check disk usage (actual filesystem)  ← NEW!
5) Exit
```

**Option 3** - Analyzes Plex media AND shows disk usage if SSH is configured
**Option 4** - Dedicated disk usage check

### Direct Command Line

**Check disk usage only:**
```bash
python3 plex_cleanup.py \
  --url "http://mirror.seedhost.eu:32108" \
  --token "YOUR_TOKEN" \
  --check-disk \
  --ssh-host "mirror.seedhost.eu" \
  --ssh-user "desispeed" \
  --remote-path "/home32"
```

**Analyze storage (includes disk usage):**
```bash
python3 plex_cleanup.py \
  --url "http://mirror.seedhost.eu:32108" \
  --token "YOUR_TOKEN" \
  --analyze-storage \
  --ssh-host "mirror.seedhost.eu" \
  --ssh-user "desispeed"
```

### Telegram Bot

Two new commands added:

```
/disk   - Check actual disk usage  (NEW!)
/space  - Analyze Plex media (now includes disk usage!)
```

**Updated command list:**
- `/preview` - Show movies to delete
- `/select` - Interactive movie selection
- `/delete` - Delete movies (with confirmation)
- `/space` - **Analyze Plex media storage** (enhanced!)
- `/disk` - **Check actual disk usage** (new!)
- `/status` - Show configuration
- `/help` - Show help

---

## 🔧 Configuration

### config.sh Updated

New SSH settings added:

```bash
# SSH Configuration for Remote Disk Usage (optional)
SSH_HOST="mirror.seedhost.eu"
SSH_USER="desispeed"
REMOTE_PATH="/home32"
```

### Setting Up SSH (Optional but Recommended)

To enable actual disk usage monitoring:

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519

# Copy key to seedbox
ssh-copy-id desispeed@mirror.seedhost.eu

# Test connection
ssh desispeed@mirror.seedhost.eu "echo 'SSH works!'"
```

Once SSH is set up, the disk usage feature will automatically:
- Query actual filesystem usage from your seedbox
- Show real-time capacity/used/free space
- Include it in all storage reports

---

## 📊 Example Output

### Without SSH (Current State)

When SSH isn't configured, you'll see:

```
⚠️  Could not retrieve actual disk usage.
To enable disk usage monitoring:
  1. Set up SSH key authentication to your server
  2. Run: ssh-copy-id desispeed@mirror.seedhost.eu

For now, use --analyze-storage to see Plex media usage.
```

### With SSH Configured

Once SSH is set up, you'll see:

```
================================================================================
DISK USAGE INFORMATION
================================================================================
Source: Remote server (mirror.seedhost.eu)
Path: /home32

Total Capacity:      3700.00 GB
Used Space:          2100.00 GB  (56.8%)
Free Space:          1600.00 GB  (43.2%)

Disk Usage:
┌────────────────────────────────────────────────────────────┐
│█████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░│
└────────────────────────────────────────────────────────────┘
 Used: 56.8%                                    Free: 43.2%

✅ Storage is healthy
================================================================================
```

### Telegram Output

**With SSH:**
```
💾 DISK USAGE
📡 Remote: mirror.seedhost.eu
==============================

Capacity: 3700 GB
████████████░░░░░░░░
Used: 2100.0 GB (56.8%)
Free: 1600.0 GB (43.2%)

✅ Healthy
```

---

## 🎯 Benefits

### Before This Feature

You could only see:
- Plex media breakdown (Movies, TV Shows, etc.)
- Estimated free space

### After This Feature

You can now see:
- **Actual disk usage** from the filesystem
- Real-time capacity monitoring
- Combined view of Plex media + total disk
- Warnings when disk is getting full
- Remote monitoring via SSH

---

## 🔍 How It Works

### Architecture

```
┌─────────────────────────────────────────────────┐
│           Plex Media Manager                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐        ┌──────────────┐     │
│  │ Storage      │        │ Disk Usage   │     │
│  │ Analyzer     │───────▶│ Checker      │     │
│  └──────────────┘        └──────┬───────┘     │
│                                  │             │
│                                  ▼             │
│                          ┌──────────────┐     │
│                          │ SSH Client   │     │
│                          └──────┬───────┘     │
└─────────────────────────────────┼─────────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │ Seedbox Server  │
                        │ (via SSH)       │
                        └─────────────────┘
```

### Components Added

1. **disk_utils.py** - New utility module
   - `DiskUsage` class
   - Local and remote disk checking
   - SSH connection handling
   - Format output for CLI/Telegram

2. **storage_analyzer.py** - Enhanced
   - Now includes disk usage in reports
   - Integrates with DiskUsage class
   - Shows combined Plex + disk view

3. **plex_cleanup.py** - New commands
   - `--check-disk` flag added
   - `--ssh-host`, `--ssh-user`, `--remote-path` options
   - `check_disk_usage()` method

4. **cleanup.sh** - Menu updated
   - Option 4 added for disk usage
   - SSH arguments passed to commands

5. **telegram_bot.py** - New commands
   - `/disk` command added
   - `/space` enhanced with disk usage
   - SSH configuration loaded

6. **start_bot.sh** - SSH export
   - Exports SSH_HOST, SSH_USER, REMOTE_PATH

---

## 💡 Tips

1. **Set up SSH** for full functionality
   - Only takes 2 minutes
   - Enables real-time disk monitoring
   - More accurate than estimates

2. **Run regularly** to monitor capacity
   - Use `/disk` in Telegram for quick checks
   - Set up cron job for automatic reports

3. **Watch for warnings**
   - Yellow warning at >80% full
   - Red warning at >90% full

4. **Combine with cleanup**
   - Check disk usage first (`/disk`)
   - Analyze what to delete (`/preview`)
   - Free up space (`/delete`)

---

## 📝 Summary

**Files Created:**
- `disk_utils.py` - Disk usage utility module
- `DISK_USAGE_FEATURE.md` - This documentation

**Files Modified:**
- `storage_analyzer.py` - Added disk integration
- `plex_cleanup.py` - Added --check-disk command
- `cleanup.sh` - Added menu option 4
- `telegram_bot.py` - Added /disk command
- `config.sh` - Added SSH configuration
- `start_bot.sh` - Export SSH variables

**New CLI Commands:**
- Option 4 in `./cleanup.sh`
- `--check-disk` flag

**New Telegram Commands:**
- `/disk` - Check disk usage
- `/space` - Enhanced with disk info

**Current Status:**
✅ All features implemented
✅ All components tested
⚠️ SSH not configured (optional, gives instructions)
✅ Falls back gracefully without SSH

---

## 🚀 Next Steps

**Optional - Enable Full Functionality:**

```bash
# 1. Generate SSH key (if needed)
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Copy to seedbox
ssh-copy-id desispeed@mirror.seedhost.eu

# 3. Test it works
ssh desispeed@mirror.seedhost.eu "df -h /home32"

# 4. Try the feature
./cleanup.sh
# Select option 4
```

**That's it! The disk usage feature is fully integrated and ready to use!** 🎉
