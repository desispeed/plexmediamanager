# Plex API Disk Usage - Now Displayed Prominently!

## ✅ Feature Added

The Plex Media Manager now shows **disk usage values from Plex API scan** at the TOP of all storage reports!

---

## 📊 What You See Now

### CLI Display

When you run `./cleanup.sh` → Option 3 (Analyze storage), you now see:

```
====================================================================================================
PLEX MEDIA DISK USAGE (from Plex API scan)
====================================================================================================
Total Media Files Scanned:   2118 files
Total Media Size:               2115.43 GB
Server Capacity:                3700.00 GB
Media Usage:                       57.2%
Available Space:                1584.57 GB (42.8%)

Plex Media Usage:
┌────────────────────────────────────────────────────────────────────────────────┐
│█████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
└────────────────────────────────────────────────────────────────────────────────┘
 Media: 57.2%                                                  Free: 42.8%

✅ Storage healthy
====================================================================================================
```

**This section appears FIRST** before the detailed breakdown!

### Telegram Display

When you send `/space` to the bot, you get:

```
💾 PLEX MEDIA DISK USAGE
📂 Scanned: 2118 files
==============================

Total Media: 2115.4 GB
Capacity: 3700 GB
Available: 1584.6 GB

Media Usage: 57.2%
███████████░░░░░░░░░

✅ Healthy
```

**Again, this appears FIRST!**

---

## 🎯 Key Information Displayed

The disk usage section shows:

1. **Total Media Files Scanned** - Count of all files in Plex
2. **Total Media Size** - Sum of all Plex media files (from API scan)
3. **Server Capacity** - Your configured total capacity (3700 GB)
4. **Media Usage %** - Percentage of capacity used by Plex media
5. **Available Space** - Free space remaining
6. **Visual Progress Bar** - Graphical representation
7. **Health Status** - ✅ Healthy / ⚠️ Warning based on usage

---

## 📈 Current Values (Your Server)

Based on the latest Plex API scan:

| Metric | Value |
|--------|-------|
| **Total Files** | 2,118 files |
| **Plex Media Size** | 2,115.43 GB |
| **Server Capacity** | 3,700.00 GB |
| **Usage** | 57.2% |
| **Available** | 1,584.57 GB (42.8%) |
| **Status** | ✅ Healthy |

### Breakdown by Type:
- **Movies**: 1,337.69 GB (118 files) - 36.2% of capacity
- **TV Shows**: 709.51 GB (479 episodes) - 19.2% of capacity
- **Training Videos**: 67.59 GB (1,455 videos) - 1.8% of capacity
- **Music**: 0.64 GB (66 tracks) - 0.0% of capacity

---

## 🔍 How It Works

### Data Source

The disk usage values come from **Plex API** by:

1. Connecting to your Plex server
2. Scanning all libraries (Movies, TV Shows, Music, Training)
3. Reading file size from each media file's metadata
4. Summing up all file sizes
5. Calculating percentages against total capacity

**This is NOT an estimate** - it's the actual sum of all media file sizes that Plex knows about.

### Formula

```
Total Media Size = Sum of all media file sizes from Plex API
Media Usage % = (Total Media Size / Server Capacity) × 100
Available Space = Server Capacity - Total Media Size
```

---

## 💡 Benefits

### Before This Update:
- Disk usage was buried in the middle of the report
- Not prominently displayed
- Easy to miss the overall picture

### After This Update:
- ✅ **Disk usage shown FIRST**
- ✅ **Clear, prominent display**
- ✅ **Visual progress bar**
- ✅ **Health status indicator**
- ✅ **File count included**
- ✅ **Works in CLI and Telegram**

---

## 🚀 Usage

### View Disk Usage - CLI

```bash
./cleanup.sh
# Select option 3
```

### View Disk Usage - Telegram

```
/space
```

### View Disk Usage - Python Direct

```bash
python3 plex_cleanup.py \
  --url "http://mirror.seedhost.eu:32108" \
  --token "YOUR_TOKEN" \
  --analyze-storage
```

---

## 📝 What Changed

### Files Modified:

**1. storage_analyzer.py**
- Added `format_cli_report()` enhancement
  - New "PLEX MEDIA DISK USAGE" section at the top
  - Shows file count, total size, capacity, usage %, available space
  - Visual progress bar
  - Health status (✅ Healthy / ⚠️ Warning)

- Updated `format_telegram_report()`
  - Same disk usage section for Telegram
  - Formatted with emojis and HTML
  - Progress bar adapted for mobile

### New Display Sections:

**CLI Format:**
```
====================================================================================================
PLEX MEDIA DISK USAGE (from Plex API scan)
====================================================================================================
[File count, sizes, percentages, bar graph, health status]
====================================================================================================
```

**Telegram Format:**
```
💾 PLEX MEDIA DISK USAGE
📂 Scanned: X files
==============================
[Sizes, percentages, progress bar, health status]
==============================
```

---

## 📊 Health Status Indicators

The system shows different status based on usage:

| Usage | Status | Display |
|-------|--------|---------|
| < 80% | Healthy | ✅ Storage healthy |
| 80-90% | Caution | ⚠️ CAUTION: Media storage over 80% of capacity |
| > 90% | Warning | ⚠️ WARNING: Media storage over 90% of capacity! |

**Your current status: ✅ Healthy (57.2%)**

---

## 🎯 Example Output

### Full CLI Output:

```
====================================================================================================
PLEX MEDIA DISK USAGE (from Plex API scan)
====================================================================================================
Total Media Files Scanned:   2118 files
Total Media Size:               2115.43 GB
Server Capacity:                3700.00 GB
Media Usage:                       57.2%
Available Space:                1584.57 GB (42.8%)

Plex Media Usage:
┌────────────────────────────────────────────────────────────────────────────────┐
│█████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
└────────────────────────────────────────────────────────────────────────────────┘
 Media: 57.2%                                                  Free: 42.8%

✅ Storage healthy
====================================================================================================

====================================================================================================
DETAILED BREAKDOWN BY MEDIA TYPE
====================================================================================================
Category                  Files      Size (GB)       % of Total   % of Used
----------------------------------------------------------------------------------------------------
Movies                    118        1337.69         36.2         63.2
TV Shows                  479        709.51          19.2         33.5
Training Videos           1455       67.59           1.8          3.2
Music                     66         0.64            0.0          0.0

[... rest of report ...]
```

### Full Telegram Output:

```
💾 PLEX MEDIA DISK USAGE
📂 Scanned: 2118 files
==============================

Total Media: 2115.4 GB
Capacity: 3700 GB
Available: 1584.6 GB

Media Usage: 57.2%
███████████░░░░░░░░░

✅ Healthy

==============================

📊 BREAKDOWN BY TYPE
==============================

🎬 Movies
   ████████████████████
   1337.7 GB (36.2%) • 118 files

📺 TV Shows
   ███████████░░░░░░░░░
   709.5 GB (19.2%) • 479 files

🎓 Training Videos
   █░░░░░░░░░░░░░░░░░░░
   67.6 GB (1.8%) • 1455 files

[... rest of report ...]
```

---

## ✅ Summary

**Feature Status: COMPLETE** ✅

- ✅ Disk usage from Plex API displayed prominently
- ✅ Shows at TOP of all storage reports
- ✅ Includes file count, sizes, percentages
- ✅ Visual progress bars
- ✅ Health status indicators
- ✅ Works in CLI, Telegram, and Python direct
- ✅ Tested and verified working

**Current Disk Usage: 2,115.43 GB / 3,700 GB (57.2%) - Healthy ✅**

The Plex Media Manager now gives you immediate visibility into disk usage from the Plex API scan!
