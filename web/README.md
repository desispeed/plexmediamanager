# Plex Media Manager - Web UI

Your Figma design system has been successfully integrated with live Plex API connection!

## 🎨 What's Included

1. **styles.css** - Complete design system with:
   - Light & Dark mode support
   - CSS custom properties (design tokens)
   - Component styles (buttons, cards, inputs, sidebar)
   - Responsive layout
   - Typography system
   - Chart colors

2. **index.html** - Dynamic dashboard with:
   - **Live Plex API data** (updates every 60 seconds)
   - Real-time storage breakdown charts
   - Actual cleanup candidates from your library
   - Quick actions
   - Settings form
   - Dark mode toggle

3. **app.py** - Flask web server with REST API:
   - `/api/stats` - Overall Plex statistics
   - `/api/storage` - Detailed storage breakdown
   - `/api/cleanup-candidates` - Movies ready for deletion
   - `/api/disk-usage` - Filesystem disk usage
   - `/api/settings` - Configuration management

4. **Deployment Files**:
   - `start_web.sh` - Quick start script
   - `plex-manager.service` - Systemd service configuration
   - `nginx.conf` - Nginx reverse proxy setup
   - `.env.example` - Environment configuration template
   - `DEPLOYMENT.md` - Complete deployment guide

## 🚀 View the Dashboard

### Option 1: Run with Live API (Recommended)

```bash
cd web
./start_web.sh
```

Then open: **http://localhost:5000**

This runs the Flask server with live Plex API data that updates automatically.

### Option 2: Static Preview

```bash
open web/index.html
```

Or double-click `index.html` in Finder (shows static data only)

## ✨ Features

### Light/Dark Mode
Click the **"🌙 Toggle Dark Mode"** button in the top-right corner.
Your preference is saved to localStorage.

### Responsive Design
- Desktop: Full sidebar + main content
- Mobile: Collapsible sidebar, stacked layout

### Design Tokens
All colors, spacing, and typography use CSS custom properties:
```css
--background
--foreground
--primary
--secondary
--muted
--accent
--destructive
--chart-1 through --chart-5
--sidebar-*
--radius
```

### Components Included

**Buttons:**
- `.btn-primary` - Main actions
- `.btn-secondary` - Secondary actions
- `.btn-destructive` - Delete/danger actions

**Cards:**
- `.card` - Content containers

**Inputs:**
- `.input` - Form inputs

**Sidebar:**
- `.sidebar` - Fixed navigation
- `.sidebar-nav-item` - Nav links with hover/active states

**Grid:**
- `.grid .grid-cols-{1-4}` - Responsive grid layouts

## 🎯 Your Actual Data

The dashboard displays your real Plex server data:

```
Total Movies:      107 (1,337.69 GB)
TV Shows:          33 (709.51 GB)
Training Videos:   23 (67.59 GB)
Storage Used:      57.2% (2,115 GB / 3,700 GB)
Available:         1,584.57 GB
Cleanup Ready:     74 movies (929 GB can be freed)
```

## 🔧 Customization

### Change Colors
Edit `styles.css` `:root` and `.dark` sections:
```css
:root {
  --primary: #your-color;
  --background: #your-bg;
}
```

### Add More Components
Use the design tokens:
```css
.my-component {
  background-color: var(--card);
  color: var(--card-foreground);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
```

### Modify Layout
The main layout uses:
```css
.sidebar (250px fixed)
.main-content (fills remaining space)
```

## 📱 Responsive Breakpoints

- Desktop: > 768px (sidebar visible)
- Mobile: ≤ 768px (sidebar hidden, grids stack)

## 🔗 Integration Options

### Option 1: Static HTML (Current)
Keep using `index.html` as a standalone dashboard

### Option 2: Integrate with Python Flask
Create a web server:
```python
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('index.html')
```

### Option 3: Connect to Plex API
Add JavaScript to fetch live data:
```javascript
fetch('/api/plex/stats')
  .then(res => res.json())
  .then(data => updateDashboard(data));
```

### Option 4: Use with Django
Integrate into Django project as templates

## 🎨 Design System Reference

### Typography Scale
```
h1: --text-2xl (1.5rem)
h2: --text-xl (1.25rem)
h3: --text-lg (1.125rem)
h4: --text-base (1rem)
body: --text-base (1rem)
small: --text-sm (0.875rem)
```

### Spacing
Uses standard multipliers: 0.5rem, 1rem, 1.5rem, 2rem

### Border Radius
```
--radius: 0.625rem (10px)
--radius-sm: 6px
--radius-md: 8px
--radius-lg: 10px
--radius-xl: 14px
```

## 🚀 Next Steps

1. **View the demo** - `open web/index.html`
2. **Test dark mode** - Click toggle button
3. **Resize browser** - Test responsive design
4. **Customize colors** - Edit `:root` in styles.css
5. **Add features** - Use design tokens for consistency

## 💡 Tips

- **Browser DevTools:** Press F12 to inspect and modify live
- **Color Picker:** Use DevTools to adjust colors visually
- **Component Library:** All styles are in `styles.css`
- **Figma Sync:** Update CSS variables to match Figma changes

## 📄 Files Structure

```
web/
├── index.html       # Dashboard demo
├── styles.css       # Design system + components
└── README.md        # This file
```

---

## 🌐 Deploy to mediamanagerdx.com

Ready to deploy to production? See the complete deployment guide:

**[📖 Read DEPLOYMENT.md](DEPLOYMENT.md)**

The deployment guide includes:
- ✅ Quick start for local testing
- ✅ Step-by-step VPS deployment (Ubuntu)
- ✅ Nginx reverse proxy configuration
- ✅ SSL certificate setup (Let's Encrypt)
- ✅ Systemd service configuration
- ✅ Environment variables guide
- ✅ Troubleshooting tips
- ✅ Security best practices

### Quick Deploy Summary:

1. **Install dependencies** on your server (Python, Nginx, Certbot)
2. **Upload files** to `/var/www/plex-manager/`
3. **Configure environment** variables in `.env`
4. **Setup systemd service** to auto-start Flask app
5. **Configure Nginx** as reverse proxy
6. **Obtain SSL certificate** with Let's Encrypt
7. **Access dashboard** at https://mediamanagerdx.com

---

## 📡 API Endpoints

Once deployed, your application exposes these REST API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Overall Plex statistics (movies, TV shows, storage) |
| `/api/storage` | GET | Detailed storage breakdown by media type |
| `/api/cleanup-candidates` | GET | List of movies ready for deletion |
| `/api/disk-usage` | GET | Actual filesystem disk usage |
| `/api/settings` | GET | Current configuration settings |

**Example API Call:**
```bash
curl https://mediamanagerdx.com/api/stats
```

---

**Your Figma design is now live with Plex API integration! Deploy to production or test locally.** 🎉
