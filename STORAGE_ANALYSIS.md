# Storage Analysis Feature

Storage usage analysis has been integrated into your Plex Manager!

## 📊 Current Storage Breakdown

Based on your 3,700 GB total capacity:

```
┌────────────────────────────────────────────────────────────┐
│ Movies:        1,337.69 GB  (36.2%)  ████████████████████   │
│ TV Shows:        709.51 GB  (19.2%)  ███████████            │
│ Training:         67.59 GB  (1.8%)   █                      │
│ Music:             0.64 GB  (0.0%)                          │
├────────────────────────────────────────────────────────────┤
│ Used:          2,115.43 GB  (57.2%)                         │
│ Free/Other:    1,584.57 GB  (42.8%)  ░░░░░░░░░░░░░░░░░      │
└────────────────────────────────────────────────────────────┘
```

**Note:** The 1,584 GB "Free/Other" includes:
- Non-Plex files (downloads, software, etc.)
- Incomplete downloads
- Free space

## 🚀 How to Use

### 1. Interactive CLI Menu

```bash
./cleanup.sh
```

Then select option **3) Analyze storage usage**

### 2. Direct Command Line

```bash
python3 plex_cleanup.py \
  --url "http://mirror.seedhost.eu:32108" \
  --token "YOUR_TOKEN" \
  --analyze-storage
```

With Telegram notification:
```bash
python3 plex_cleanup.py \
  --url "http://mirror.seedhost.eu:32108" \
  --token "YOUR_TOKEN" \
  --analyze-storage \
  --telegram-token "YOUR_BOT_TOKEN" \
  --telegram-chat-id "YOUR_CHAT_ID" \
  --send-telegram
```

### 3. Telegram Bot

Send the command:
```
/space
```

The bot will respond with a formatted storage report with emojis and progress bars!

## 📱 Telegram Bot Commands (Updated)

```
/start    - Show help and available commands
/preview  - Show movies that would be deleted
/select   - Select movies interactively with buttons
/delete   - Delete movies (with confirmation)
/space    - 💾 Analyze storage usage (NEW!)
/status   - Show current configuration
/help     - Show help message
```

## 🔧 Features

- **Visual Progress Bars**: See storage usage at a glance
- **Category Breakdown**: Movies, TV Shows, Music, Training Videos
- **Percentage Analysis**: Both of total capacity and used space
- **Telegram Integration**: Get reports sent to your phone
- **CLI-Friendly**: Beautiful terminal output with Unicode graphics

## 💡 Tips

1. **Run before cleanup**: Check storage before deciding what to delete
2. **Track progress**: Run after deletions to see space freed
3. **Monitor capacity**: Get warned when storage is >80% full
4. **Automate**: Add to cron jobs with `--send-telegram` for reports

## 🎯 What's Next?

If you set up SSH access to your seedbox, we can:
- Scan non-Plex files in Downloads folder
- Identify software, incomplete downloads
- Find the exact breakdown of that 1,584 GB "Other" space
- Clean up duplicate files

## 📈 Example Output

**CLI:**
```
====================================================================================================
STORAGE BREAKDOWN BY CATEGORY
====================================================================================================
Category                  Files      Size (GB)       % of Total   % of Used
----------------------------------------------------------------------------------------------------
Movies                    118        1337.69         36.2         63.2
TV Shows                  479        709.51          19.2         33.5
Training Videos           1455       67.59           1.8          3.2
Music                     66         0.64            0.0          0.0
```

**Telegram:**
```
💾 STORAGE ANALYSIS
📊 Total Capacity: 3700 GB
==============================

🎬 Movies
   ████████████████████
   1337.7 GB (36.2%) • 118 files

📺 TV Shows
   ███████████░░░░░░░░░
   709.5 GB (19.2%) • 479 files

✨ Free Space
   ░░░░░░░░░░░░░░░░░░░░
   1584.6 GB (42.8%)
```

---

**Enjoy your new storage analysis feature!**
