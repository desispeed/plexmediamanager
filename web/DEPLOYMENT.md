# Plex Media Manager - Deployment Guide

Complete guide for deploying the Plex Media Manager to **mediamanagerdx.com**

---

## 📋 Table of Contents

1. [Quick Start - Local Development](#quick-start---local-development)
2. [Production Deployment Options](#production-deployment-options)
3. [Deploy to VPS/Cloud Server](#deploy-to-vpscloud-server)
4. [Deploy to Existing Server](#deploy-to-existing-server)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start - Local Development

Test the web application locally before deploying to production:

### 1. Install Dependencies

```bash
cd web
pip3 install -r ../requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 3. Start the Server

```bash
./start_web.sh
```

The dashboard will be available at: **http://localhost:5000**

### 4. Test the Dashboard

Open your browser and navigate to:
- **Dashboard**: http://localhost:5000
- **API Stats**: http://localhost:5000/api/stats
- **API Storage**: http://localhost:5000/api/storage
- **Cleanup Candidates**: http://localhost:5000/api/cleanup-candidates

---

## 🌐 Production Deployment Options

### Option 1: Deploy to VPS/Cloud Server (Recommended)

Best for: Standalone deployment with full control

**Supported Platforms:**
- DigitalOcean Droplet
- AWS EC2
- Linode
- Vultr
- Any VPS with Ubuntu/Debian

### Option 2: Deploy to Existing Web Server

Best for: Adding to existing website infrastructure

**Supported Servers:**
- Apache with mod_proxy
- Nginx with reverse proxy
- Caddy

### Option 3: Deploy with Docker

Best for: Containerized deployment

---

## 🖥️ Deploy to VPS/Cloud Server

Complete step-by-step guide for deploying to a fresh Ubuntu 22.04 server.

### Prerequisites

- Ubuntu 22.04 LTS server
- Root or sudo access
- Domain pointing to server IP (mediamanagerdx.com)

### Step 1: Server Setup

```bash
# Connect to your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip nginx certbot python3-certbot-nginx git
```

### Step 2: Create Application Directory

```bash
# Create directory
mkdir -p /var/www/plex-manager
cd /var/www/plex-manager

# Clone or upload your files
# Option A: If using Git
git clone https://github.com/yourusername/plex-cleanup.git .

# Option B: Upload files via SCP
# On your local machine:
scp -r /path/to/plex-cleanup/web root@your-server-ip:/var/www/plex-manager/
```

### Step 3: Install Python Dependencies

```bash
cd /var/www/plex-manager
pip3 install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cd web
cp .env.example .env
nano .env
```

**Edit .env with your settings:**

```env
PLEX_URL=http://mirror.seedhost.eu:32108
PLEX_TOKEN=j89Uh7HxZfGPEj3nkq9Z
TOTAL_CAPACITY_GB=3700
SSH_HOST=mirror.seedhost.eu
SSH_USER=desispeed
REMOTE_PATH=/home32
PORT=5000
FLASK_DEBUG=False
FLASK_ENV=production
```

### Step 5: Setup Systemd Service

```bash
# Copy service file
cp /var/www/plex-manager/web/plex-manager.service /etc/systemd/system/

# Edit service file if paths are different
nano /etc/systemd/system/plex-manager.service

# Reload systemd
systemctl daemon-reload

# Enable and start service
systemctl enable plex-manager
systemctl start plex-manager

# Check status
systemctl status plex-manager
```

### Step 6: Configure Nginx

```bash
# Copy nginx configuration
cp /var/www/plex-manager/web/nginx.conf /etc/nginx/sites-available/plex-manager

# Create symbolic link
ln -s /etc/nginx/sites-available/plex-manager /etc/nginx/sites-enabled/

# Test nginx configuration
nginx -t

# Reload nginx
systemctl reload nginx
```

### Step 7: Setup SSL Certificate

```bash
# Obtain SSL certificate from Let's Encrypt
certbot --nginx -d mediamanagerdx.com -d www.mediamanagerdx.com

# Follow the prompts to complete setup
```

### Step 8: Verify Deployment

Visit **https://mediamanagerdx.com** in your browser!

---

## 🔧 Deploy to Existing Server

If you already have a web server running on mediamanagerdx.com:

### For Nginx

```bash
# Add to existing nginx configuration
nano /etc/nginx/sites-available/mediamanagerdx.com
```

Add this location block:

```nginx
location /plex {
    proxy_pass http://127.0.0.1:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}

location /api {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

Then reload nginx:

```bash
systemctl reload nginx
```

Dashboard will be available at: **https://mediamanagerdx.com/plex**

### For Apache

```bash
# Enable required modules
a2enmod proxy proxy_http

# Add to your Apache configuration
nano /etc/apache2/sites-available/mediamanagerdx.com.conf
```

Add:

```apache
<Location /plex>
    ProxyPass http://127.0.0.1:5000
    ProxyPassReverse http://127.0.0.1:5000
</Location>

<Location /api>
    ProxyPass http://127.0.0.1:5000/api
    ProxyPassReverse http://127.0.0.1:5000/api
</Location>
```

Then restart Apache:

```bash
systemctl restart apache2
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PLEX_URL` | Plex server URL | http://mirror.seedhost.eu:32108 | ✅ Yes |
| `PLEX_TOKEN` | Plex authentication token | - | ✅ Yes |
| `TOTAL_CAPACITY_GB` | Total storage capacity in GB | 3700 | ✅ Yes |
| `SSH_HOST` | SSH host for remote disk usage | - | ❌ No |
| `SSH_USER` | SSH username | - | ❌ No |
| `REMOTE_PATH` | Remote path to check | /home32 | ❌ No |
| `PORT` | Web server port | 5000 | ✅ Yes |
| `FLASK_DEBUG` | Enable debug mode | False | ✅ Yes |
| `FLASK_ENV` | Flask environment | production | ✅ Yes |

### Getting Your Plex Token

1. Open Plex Web App
2. Navigate to any media item
3. Click "Get Info" → "View XML"
4. Look for `X-Plex-Token` in the URL

**Example:** `...?X-Plex-Token=j89Uh7HxZfGPEj3nkq9Z`

---

## 🔍 API Endpoints

The application provides the following REST API endpoints:

### GET /api/stats
Returns overall Plex statistics

**Response:**
```json
{
  "total_movies": 107,
  "total_movies_size_gb": 1337.69,
  "total_tv_shows": 33,
  "total_tv_shows_size_gb": 709.51,
  "storage_used_gb": 2115.43,
  "storage_capacity_gb": 3700,
  "storage_used_percent": 57.2,
  "storage_available_gb": 1584.57,
  "storage_available_percent": 42.8
}
```

### GET /api/storage
Returns detailed storage breakdown by media type

**Response:**
```json
{
  "total_files": 2118,
  "total_used_gb": 2115.43,
  "capacity_gb": 3700,
  "used_percentage": 57.2,
  "available_gb": 1584.57,
  "breakdown": [
    {
      "category": "Movies",
      "files": 107,
      "size_gb": 1337.69,
      "percent_of_total": 36.2,
      "percent_of_used": 63.2
    }
  ]
}
```

### GET /api/cleanup-candidates
Returns list of movies that can be deleted

**Query Parameters:**
- `max_view_count` (default: 1) - Maximum view count
- `days_not_watched` (default: 30) - Days since last watched

**Response:**
```json
{
  "total_candidates": 74,
  "total_size_gb": 929.12,
  "candidates": [
    {
      "title": "Good Boy",
      "year": 2025,
      "size_gb": 13.1,
      "view_count": 0,
      "last_viewed": "Never",
      "days_since_watched": null
    }
  ]
}
```

### GET /api/disk-usage
Returns actual filesystem disk usage

**Response:**
```json
{
  "total_gb": 3700,
  "used_gb": 2115.43,
  "free_gb": 1584.57,
  "percent_used": 57.2,
  "source": "remote"
}
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check service logs
journalctl -u plex-manager -n 50 --no-pager

# Check if port is already in use
sudo lsof -i :5000

# Test Flask app directly
cd /var/www/plex-manager/web
python3 app.py
```

### Nginx 502 Bad Gateway

```bash
# Check if Flask app is running
systemctl status plex-manager

# Check nginx error logs
tail -f /var/log/nginx/plex-manager-error.log

# Restart services
systemctl restart plex-manager
systemctl restart nginx
```

### Cannot Connect to Plex

```bash
# Test Plex connection
curl "http://mirror.seedhost.eu:32108?X-Plex-Token=YOUR_TOKEN"

# Check firewall rules
sudo ufw status

# Verify environment variables
cat /var/www/plex-manager/web/.env
```

### SSL Certificate Issues

```bash
# Renew certificate
certbot renew

# Test certificate
certbot certificates

# Force renewal
certbot renew --force-renewal
```

### Static Files Not Loading

```bash
# Check file permissions
ls -la /var/www/plex-manager/web/

# Fix permissions
chown -R www-data:www-data /var/www/plex-manager/web/
chmod -R 755 /var/www/plex-manager/web/
```

---

## 📊 Monitoring & Maintenance

### View Service Logs

```bash
# Real-time logs
journalctl -u plex-manager -f

# Last 100 lines
journalctl -u plex-manager -n 100

# Logs from today
journalctl -u plex-manager --since today
```

### Restart Service

```bash
systemctl restart plex-manager
```

### Update Application

```bash
cd /var/www/plex-manager
git pull  # If using git
systemctl restart plex-manager
```

### Auto-restart on Failure

The systemd service is configured to automatically restart if it crashes:

```ini
Restart=always
RestartSec=10
```

---

## 🔐 Security Best Practices

1. **Use HTTPS**: Always use SSL certificates (Let's Encrypt is free)
2. **Firewall**: Only open necessary ports (80, 443, 22)
3. **Authentication**: Consider adding HTTP basic auth or OAuth
4. **Updates**: Keep system and dependencies updated
5. **Backups**: Regular backups of configuration files
6. **SSH Keys**: Use SSH keys instead of passwords

### Add HTTP Basic Auth (Optional)

```bash
# Install apache2-utils
apt install apache2-utils

# Create password file
htpasswd -c /etc/nginx/.htpasswd admin

# Add to nginx configuration
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

---

## 📁 File Structure

```
/var/www/plex-manager/
├── web/
│   ├── app.py                  # Flask application
│   ├── index.html              # Dashboard frontend
│   ├── styles.css              # Figma design system
│   ├── .env                    # Environment variables (not in git)
│   ├── .env.example            # Example environment file
│   ├── start_web.sh            # Startup script
│   ├── plex-manager.service    # Systemd service file
│   ├── nginx.conf              # Nginx configuration
│   └── DEPLOYMENT.md           # This file
├── plex_cleanup.py             # Core cleanup engine
├── storage_analyzer.py         # Storage analysis module
├── disk_utils.py               # Disk usage utilities
└── requirements.txt            # Python dependencies
```

---

## 🎯 Quick Deployment Checklist

- [ ] Server provisioned (Ubuntu 22.04)
- [ ] Domain configured (A record pointing to server IP)
- [ ] Dependencies installed (Python, Nginx, Certbot)
- [ ] Application files uploaded
- [ ] Python packages installed (`pip3 install -r requirements.txt`)
- [ ] Environment variables configured (`.env` file)
- [ ] Systemd service created and started
- [ ] Nginx configuration added
- [ ] SSL certificate obtained
- [ ] Firewall configured (ports 80, 443)
- [ ] Dashboard accessible via HTTPS
- [ ] API endpoints working
- [ ] Service auto-starts on reboot

---

## 📞 Support

For issues or questions:
- Check logs: `journalctl -u plex-manager -n 50`
- Test API directly: `curl http://localhost:5000/api/stats`
- Review Plex connection: Verify URL and token in `.env`

---

**Your Plex Media Manager is now ready for deployment to mediamanagerdx.com!** 🎉
