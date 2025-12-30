# Plex Media Manager - Docker Deployment

## ✅ Container Successfully Started!

The **plex-manager** Docker container is now running and ready for deployment to mediamanagerdx.com.

---

## 📦 Container Status

**Container Name:** `plex-manager`
**Status:** ✅ Running
**Port:** 5002 (host) → 5000 (container)
**Health Check:** Enabled (checks `/api/stats` endpoint)
**Restart Policy:** `unless-stopped`

**Access URLs:**
- **Dashboard:** http://localhost:5002
- **API:** http://localhost:5002/api/*

---

## 🔍 Verify Container

```bash
# Check container status
docker ps | grep plex-manager

# View container logs
docker logs plex-manager

# Follow logs in real-time
docker logs -f plex-manager

# Check health status
docker inspect plex-manager | grep -A 10 Health
```

---

## 🎯 Current Configuration

**Environment Variables:**
```env
PLEX_URL=http://mirror.seedhost.eu:32108
PLEX_TOKEN=j89Uh7HxZfGPEj3nkq9Z
TOTAL_CAPACITY_GB=3700
SSH_HOST=mirror.seedhost.eu
SSH_USER=desispeed
REMOTE_PATH=/home32
PORT=5000
FLASK_ENV=production
```

**Volumes:**
- Application code mounted as read-only
- Hot-reload enabled during development

---

## 🚀 Container Management

### Start Container
```bash
docker-compose up -d
```

### Stop Container
```bash
docker-compose down
```

### Restart Container
```bash
docker-compose restart
```

### Rebuild and Start
```bash
docker-compose up -d --build
```

### View Logs
```bash
# Last 100 lines
docker logs --tail 100 plex-manager

# Follow logs
docker logs -f plex-manager

# With timestamps
docker logs -t plex-manager
```

### Update Container
```bash
# Pull latest changes
git pull

# Rebuild image
docker-compose build

# Restart with new image
docker-compose up -d
```

---

## 🌐 Deploy to Production (mediamanagerdx.com)

### Option 1: Deploy to Cloud Server

**1. Upload to Server:**
```bash
# From your local machine
scp -r /path/to/plex-cleanup user@mediamanagerdx.com:/var/www/
```

**2. SSH to Server:**
```bash
ssh user@mediamanagerdx.com
cd /var/www/plex-cleanup
```

**3. Configure Environment:**
```bash
# Edit environment variables if needed
nano .env
```

**4. Start Container:**
```bash
docker-compose up -d
```

**5. Configure Nginx Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name mediamanagerdx.com;

    location / {
        proxy_pass http://localhost:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**6. Get SSL Certificate:**
```bash
sudo certbot --nginx -d mediamanagerdx.com
```

### Option 2: Docker Hub Deployment

**1. Tag and Push Image:**
```bash
# Tag image
docker tag plex-cleanup-plex-manager yourusername/plex-manager:latest

# Push to Docker Hub
docker push yourusername/plex-manager:latest
```

**2. Pull on Server:**
```bash
# On mediamanagerdx.com server
docker pull yourusername/plex-manager:latest

# Run container
docker run -d \
  --name plex-manager \
  --restart unless-stopped \
  -p 5002:5000 \
  -e PLEX_URL="http://mirror.seedhost.eu:32108" \
  -e PLEX_TOKEN="j89Uh7HxZfGPEj3nkq9Z" \
  -e TOTAL_CAPACITY_GB=3700 \
  yourusername/plex-manager:latest
```

---

## 📊 Test Container APIs

```bash
# Test statistics endpoint
curl http://localhost:5002/api/stats | jq

# Test storage breakdown
curl http://localhost:5002/api/storage | jq

# Test cleanup candidates
curl http://localhost:5002/api/cleanup-candidates | jq

# Test disk usage
curl http://localhost:5002/api/disk-usage | jq

# Test settings
curl http://localhost:5002/api/settings | jq
```

---

## 🔒 Security Considerations

**For Production Deployment:**

1. **Use Environment Files:**
   ```bash
   # Don't commit .env to git
   echo ".env" >> .gitignore
   ```

2. **Use Secrets:**
   ```yaml
   # docker-compose.yml
   secrets:
     plex_token:
       external: true
   ```

3. **Enable HTTPS:**
   - Use Let's Encrypt SSL certificates
   - Configure Nginx with SSL
   - Redirect HTTP to HTTPS

4. **Limit Network Access:**
   ```yaml
   networks:
     plex-network:
       internal: true
   ```

5. **Run as Non-Root User:**
   ```dockerfile
   # In Dockerfile
   RUN useradd -m appuser
   USER appuser
   ```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs plex-manager

# Check if port is already in use
lsof -i :5002

# Recreate container
docker-compose down
docker-compose up -d
```

### API Returns Errors

```bash
# Check environment variables
docker exec plex-manager env | grep PLEX

# Test Plex connection from inside container
docker exec plex-manager curl -s "$PLEX_URL"

# Restart container
docker-compose restart
```

### Health Check Failing

```bash
# Check health status
docker inspect plex-manager --format='{{json .State.Health}}' | jq

# Test health endpoint manually
curl http://localhost:5002/api/stats

# View detailed logs
docker logs plex-manager
```

### Container Keeps Restarting

```bash
# Check logs for errors
docker logs plex-manager --tail 50

# Check resource usage
docker stats plex-manager

# Inspect container state
docker inspect plex-manager
```

---

## 📁 Files Created

**Docker Files:**
- ✅ `Dockerfile` - Container image definition
- ✅ `docker-compose.yml` - Container orchestration
- ✅ `.env` - Environment variables
- ✅ `.dockerignore` - Files to exclude from build

**Documentation:**
- ✅ `DOCKER_DEPLOYMENT.md` - This file

---

## 🎊 Current Status

**Container:** ✅ Running on port 5002
**API:** ✅ All endpoints working
**Dashboard:** ✅ Accessible at http://localhost:5002
**Health Check:** ✅ Enabled and passing

**Test Results:**
```json
{
    "storage_available_gb": 1584.57,
    "storage_available_percent": 42.8,
    "storage_capacity_gb": 3700.0,
    "storage_used_gb": 2115.43,
    "storage_used_percent": 57.2,
    "total_movies": 118,
    "total_movies_size_gb": 1337.69,
    "total_tv_shows": 479,
    "total_tv_shows_size_gb": 709.51
}
```

---

## 🚢 Next Steps

1. **Test Locally:** http://localhost:5002
2. **Deploy to Server:** Follow production deployment steps above
3. **Configure Domain:** Point mediamanagerdx.com to server
4. **Setup SSL:** Use certbot for HTTPS
5. **Monitor:** Use `docker logs -f plex-manager`

---

## 📞 Quick Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker logs -f plex-manager

# Status
docker ps | grep plex-manager

# Rebuild
docker-compose up -d --build

# Shell access
docker exec -it plex-manager /bin/bash
```

---

**Your Plex Media Manager is now containerized and ready for deployment to mediamanagerdx.com! 🎉**
