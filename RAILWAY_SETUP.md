# Railway Persistent Storage Setup

## Problem
User authentication data was being lost on each deployment because Railway's filesystem is ephemeral.

## Solution
Set up Railway's persistent volume to store user data across deployments.

## Steps to Configure Railway Persistent Storage

### 1. In Railway Dashboard

1. Go to your project: https://railway.app/project/[your-project-id]
2. Click on your service (backend API)
3. Go to **Settings** tab
4. Scroll to **Volumes** section
5. Click **+ New Volume**
6. Configure the volume:
   - **Mount Path**: `/data`
   - **Size**: 5 GB (Railway default - more than sufficient for user data)
7. Click **Add**

### 2. Set Environment Variable

In Railway Settings → Variables, add:
```
DATA_DIR=/data
```

This tells the auth system to store users.json in the persistent volume.

### 3. Redeploy

After adding the volume and environment variable, Railway will automatically redeploy.
Your user data will now persist across all future deployments!

## Verification

After setup, check that data persists:

1. Register a user on https://mediamanagerdx.com/register
2. Trigger a redeploy (push new code to GitHub)
3. Try logging in - your user should still exist

## Docker Local Development

For local Docker development, the data is persisted using a Docker named volume:
- Volume name: `plex-manager-data`
- Mount path: `/data`
- Location: Managed by Docker

To view persisted data:
```bash
docker volume inspect plex-manager-data
docker exec -it plex-manager ls -la /data
```

## Backup User Data

### From Railway:
```bash
# Using Railway CLI
railway run cat /data/users.json > users_backup.json
```

### From Docker:
```bash
# Copy from container
docker cp plex-manager:/data/users.json users_backup.json
```

## Restore User Data

### To Railway:
```bash
# Using Railway CLI
railway run sh -c 'cat > /data/users.json' < users_backup.json
```

### To Docker:
```bash
# Copy to container
docker cp users_backup.json plex-manager:/data/users.json
```
