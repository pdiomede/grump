# Deployment Guide - Ubuntu VPS with Nginx

This guide walks you through deploying The Graph Council Voting Monitor on an Ubuntu VPS with Nginx as the web server.

## Prerequisites

- Ubuntu server (20.04 LTS or newer recommended)
- Root or sudo access
- Domain name (optional, but recommended)
- SSH access to your VPS

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│  Cron Job (runs every 24 hours)            │
│  └─> Python Script                          │
│      └─> Generates index.html              │
│          └─> Saved to /var/www/grump/      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Nginx Web Server                           │
│  └─> Serves index.html                      │
│      └─> Accessible via browser             │
└─────────────────────────────────────────────┘
```

## Step 1: Server Preparation

### 1.1 Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Install Required Packages

```bash
# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Nginx
sudo apt install -y nginx

# Install Git (if needed)
sudo apt install -y git

# Optional: Install certbot for HTTPS
sudo apt install -y certbot python3-certbot-nginx
```

## Step 2: Create Application User

Create a dedicated user for security (optional but recommended):

```bash
sudo useradd -m -s /bin/bash grump
sudo usermod -aG www-data grump
```

## Step 3: Deploy Application

### 3.1 Create Application Directory

```bash
# Create directory
sudo mkdir -p /opt/grump
sudo chown grump:grump /opt/grump

# Switch to grump user
sudo su - grump
```

### 3.2 Upload/Clone Project Files

**Option A: Using Git**
```bash
cd /opt/grump
git clone https://github.com/yourusername/grump.git .
```

**Option B: Using SCP (from your local machine)**
```bash
# Run this on your LOCAL machine
scp -r /Users/pdiomede/Documents/WORK/_coding/controldeck/grump/* user@your-vps-ip:/opt/grump/
```

**Option C: Manual Upload**
Use an FTP client (FileZilla, Cyberduck) to upload files to `/opt/grump/`

### 3.3 Set Up Python Environment

```bash
cd /opt/grump

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3.4 Configure Environment

```bash
# Copy and edit .env file
cp .env.example .env
nano .env
```

Update `.env` with your settings:
```env
SNAPSHOT_SPACE=council.graphprotocol.eth
ALERT_THRESHOLD_DAYS=5
WALLETS_FILE=/opt/grump/wallets.txt
OUTPUT_HTML=/var/www/grump/index.html
```

### 3.5 Configure Wallet Addresses

```bash
nano wallets.txt
```

Add your council member wallet addresses (one per line):
```
0xAddress1...
0xAddress2...
0xAddress3...
0xAddress4...
0xAddress5...
0xAddress6...
```

### 3.6 Test the Script

```bash
# Make sure virtual environment is activated
source /opt/grump/venv/bin/activate

# Run the script
python3 monitor_council_votes.py
```

If successful, you should see output confirming the script ran.

## Step 4: Configure Web Directory

### 4.1 Create Web Directory

```bash
# Exit from grump user back to your sudo user
exit

# Create web directory
sudo mkdir -p /var/www/grump
sudo chown grump:www-data /var/www/grump
sudo chmod 775 /var/www/grump
```

### 4.2 Run Initial Generation

```bash
sudo su - grump
cd /opt/grump
source venv/bin/activate
python3 monitor_council_votes.py
exit
```

Verify the HTML file was created:
```bash
ls -la /var/www/grump/index.html
```

## Step 5: Configure Nginx

### 5.1 Create Nginx Site Configuration

```bash
sudo nano /etc/nginx/sites-available/grump
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or VPS IP
    
    root /var/www/grump;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Cache static content
    location ~* \.(html|css|js)$ {
        expires 1h;
        add_header Cache-Control "public, must-revalidate, proxy-revalidate";
    }
    
    # Access logs
    access_log /var/log/nginx/grump_access.log;
    error_log /var/log/nginx/grump_error.log;
}
```

### 5.2 Enable Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/grump /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 5.3 Allow Firewall (if UFW is enabled)

```bash
sudo ufw allow 'Nginx Full'
sudo ufw status
```

## Step 6: Set Up Automated Execution

### 6.1 Create Wrapper Script

```bash
sudo nano /opt/grump/run_cron.sh
```

Add the following content:

```bash
#!/bin/bash
# Wrapper script for cron execution

# Change to script directory
cd /opt/grump

# Activate virtual environment
source /opt/grump/venv/bin/activate

# Run the monitor
/opt/grump/venv/bin/python3 /opt/grump/monitor_council_votes.py

# Log completion
echo "Monitor run completed at $(date)" >> /var/log/grump/cron.log
```

Make it executable:
```bash
sudo chmod +x /opt/grump/run_cron.sh
sudo chown grump:grump /opt/grump/run_cron.sh
```

### 6.2 Create Log Directory

```bash
sudo mkdir -p /var/log/grump
sudo chown grump:grump /var/log/grump
```

### 6.3 Configure Cron Job

```bash
# Edit crontab for grump user
sudo crontab -u grump -e
```

Add one of the following lines:

**Run daily at 9:00 AM UTC:**
```cron
0 9 * * * /opt/grump/run_cron.sh >> /var/log/grump/output.log 2>&1
```

**Run every 24 hours from now:**
```cron
0 */24 * * * /opt/grump/run_cron.sh >> /var/log/grump/output.log 2>&1
```

**Run twice daily (9 AM and 9 PM UTC):**
```cron
0 9,21 * * * /opt/grump/run_cron.sh >> /var/log/grump/output.log 2>&1
```

Save and exit.

### 6.4 Verify Cron Setup

```bash
# List cron jobs for grump user
sudo crontab -u grump -l

# Check cron service is running
sudo systemctl status cron
```

## Step 7: Set Up HTTPS (Optional but Recommended)

### 7.1 Using Let's Encrypt (Free SSL Certificate)

**Prerequisites:**
- Domain name pointing to your VPS IP
- Ports 80 and 443 open

```bash
# Install Certbot (if not already installed)
sudo apt install -y certbot python3-certbot-nginx

# Obtain and install certificate
sudo certbot --nginx -d your-domain.com

# Follow the prompts
```

Certbot will automatically:
- Obtain SSL certificate
- Update Nginx configuration
- Set up auto-renewal

### 7.2 Test Auto-Renewal

```bash
sudo certbot renew --dry-run
```

## Step 8: Monitoring and Maintenance

### 8.1 Check Logs

```bash
# Monitor cron execution logs
tail -f /var/log/grump/output.log

# Monitor cron activity logs
tail -f /var/log/grump/cron.log

# Check Nginx access logs
sudo tail -f /var/log/nginx/grump_access.log

# Check Nginx error logs
sudo tail -f /var/log/nginx/grump_error.log

# Check system cron logs
sudo tail -f /var/log/syslog | grep CRON
```

### 8.2 Manual Script Execution

```bash
sudo su - grump
cd /opt/grump
source venv/bin/activate
python3 monitor_council_votes.py
exit
```

### 8.3 Log Rotation

Create log rotation configuration:

```bash
sudo nano /etc/logrotate.d/grump
```

Add:
```
/var/log/grump/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 grump grump
}
```

## Step 9: Security Hardening

### 9.1 Restrict Web Access (Optional)

If you want to restrict access to specific IP addresses:

```bash
sudo nano /etc/nginx/sites-available/grump
```

Add inside the `server` block:
```nginx
# Allow specific IPs only
allow 1.2.3.4;      # Your office IP
allow 5.6.7.8;      # Your home IP
deny all;
```

### 9.2 Set Up HTTP Basic Authentication (Optional)

```bash
# Install apache2-utils for htpasswd
sudo apt install -y apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Update Nginx config
sudo nano /etc/nginx/sites-available/grump
```

Add inside `location /`:
```nginx
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

Reload Nginx:
```bash
sudo systemctl reload nginx
```

## Step 10: Access Your Monitor

### Via Browser

**HTTP:**
```
http://your-vps-ip/
http://your-domain.com/
```

**HTTPS:**
```
https://your-domain.com/
```

## Troubleshooting

### Issue: HTML not being generated

**Check:**
```bash
# Test script manually
sudo su - grump
cd /opt/grump
source venv/bin/activate
python3 monitor_council_votes.py
```

**Common causes:**
- Missing dependencies: `pip install -r requirements.txt`
- Wrong permissions on output directory
- Network issues accessing Snapshot API

### Issue: Nginx 404 Error

**Check:**
```bash
# Verify file exists
ls -la /var/www/grump/index.html

# Check Nginx configuration
sudo nginx -t

# Check Nginx error logs
sudo tail -50 /var/log/nginx/grump_error.log
```

### Issue: Cron job not running

**Check:**
```bash
# Verify cron service is running
sudo systemctl status cron

# Check cron logs
sudo tail -100 /var/log/syslog | grep CRON

# Check script logs
tail -50 /var/log/grump/output.log

# Test wrapper script manually
sudo su - grump
/opt/grump/run_cron.sh
```

### Issue: Permission Denied

**Fix permissions:**
```bash
sudo chown -R grump:grump /opt/grump
sudo chown grump:www-data /var/www/grump
sudo chmod 775 /var/www/grump
```

## Maintenance Commands

### Update the Application

```bash
sudo su - grump
cd /opt/grump
git pull  # If using git
source venv/bin/activate
pip install -r requirements.txt --upgrade
exit
```

### Restart Nginx

```bash
sudo systemctl restart nginx
```

### View Real-time Logs

```bash
# Application logs
tail -f /var/log/grump/output.log

# Nginx logs
sudo tail -f /var/log/nginx/grump_access.log
```

### Check Disk Space

```bash
df -h
du -sh /var/log/grump/*
```

## Backup Recommendations

### Files to Backup

- `/opt/grump/.env` - Configuration
- `/opt/grump/wallets.txt` - Council member addresses
- `/etc/nginx/sites-available/grump` - Nginx config

### Backup Script Example

```bash
#!/bin/bash
BACKUP_DIR="/backup/grump"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/grump-config-$DATE.tar.gz \
    /opt/grump/.env \
    /opt/grump/wallets.txt \
    /etc/nginx/sites-available/grump
```

## Performance Optimization

### Enable Gzip Compression

Add to `/etc/nginx/nginx.conf` in the `http` block:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/html application/javascript;
```

### Add Browser Caching

Already included in the Nginx configuration above. Adjust `expires` value as needed.

## Support

For issues or questions:
- Check logs: `/var/log/grump/`
- Test script manually: `python3 monitor_council_votes.py`
- Verify Nginx config: `sudo nginx -t`
- Review this deployment guide

---

**Deployment Complete!** 🚀

Your Graph Council Voting Monitor should now be accessible via your domain/IP and automatically updating every 24 hours.

