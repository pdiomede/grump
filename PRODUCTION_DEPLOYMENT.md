# 🚀 Production Deployment Guide

Quick reference for deploying authentication to your VPS.

## 📦 Files Location on VPS

Your uploaded files are at: `/home/graph/ftpbox/grump/`

## 🎯 One-Command Deployment

```bash
# Run the deployment script
sudo bash /home/graph/ftpbox/grump/deploy_auth_to_production.sh
```

This script will:
- ✅ Create necessary directories
- ✅ Copy files to production locations
- ✅ Set correct permissions
- ✅ Install systemd service
- ✅ Install Python dependencies

## 📍 Production File Locations

After deployment:

```
/var/www/grump-config/          # Config directory
├── auth_gate.py                # Auth server
├── allowed_people.txt          # Email whitelist
├── .env.example                # Config template
└── .env                        # YOUR CREDENTIALS (you create this)

/var/www/iproot/grump/          # Web root
├── login.html                  # Login page
├── index.html                  # Dashboard
├── monitor_council_votes.py    # Dashboard generator
└── logs/
    └── auth_gateway.log        # Auth logs
```

## 🔧 Post-Deployment Steps

### 1. Create .env File

```bash
# Generate cookie secret
python3 -c "import os; print(os.urandom(32).hex())"

# Create .env file
sudo nano /var/www/grump-config/.env
```

Add this content (replace with your real values):

```env
# Cookie secret (paste generated value above)
AUTH_COOKIE_SECRET=<your-64-char-secret>

# Gmail SMTP (use App Password!)
# Get App Password: https://myaccount.google.com/apppasswords
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM=your-email@gmail.com

# Production URL
DASHBOARD_URL=https://dashboards.thegraph.foundation/grump/
```

**Set secure permissions:**
```bash
sudo chmod 600 /var/www/grump-config/.env
sudo chown www-data:www-data /var/www/grump-config/.env
```

### 2. Configure Whitelist

```bash
sudo nano /var/www/grump-config/allowed_people.txt
```

Add authorized emails:
```
*@thegraph.foundation
*@edgeandnode.com
specific-user@example.com
```

### 3. Configure Nginx

Edit your Nginx config:
```bash
sudo nano /etc/nginx/sites-available/dashboards.thegraph.foundation.conf
```

Add/update the `/grump/` location block:

```nginx
location /grump/ {
    # Proxy to auth gateway on port 38081
    proxy_pass http://127.0.0.1:38081/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cookie_path / /grump/;
}
```

**Test and reload:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Start Auth Service

```bash
# Enable on boot
sudo systemctl enable grump_auth.service

# Start now
sudo systemctl start grump_auth.service

# Check status
sudo systemctl status grump_auth.service
```

### 5. Test the System

Visit: https://dashboards.thegraph.foundation/grump/

You should see:
1. ✅ Login page appears
2. ✅ Can enter email
3. ✅ Receive OTP code via email
4. ✅ Can login with code
5. ✅ Dashboard loads

## 📊 Monitoring Commands

```bash
# View service status
sudo systemctl status grump_auth.service

# View real-time logs
sudo journalctl -u grump_auth.service -f

# View log file
tail -f /var/www/iproot/grump/logs/auth_gateway.log

# Check if port 38081 is listening
sudo lsof -i :38081

# Restart service
sudo systemctl restart grump_auth.service
```

## 🐛 Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u grump_auth.service -n 50

# Test manually as www-data user
sudo -u www-data python3 /var/www/grump-config/auth_gate.py
```

### Email not sending

```bash
# Test SMTP connection
python3 -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls()"
```

**Check:**
- Using Gmail App Password (not regular password)
- SMTP credentials correct in `.env`
- Firewall allows outbound SMTP (port 587)

### Can't access dashboard

**Check:**
- Nginx config has proxy_pass to port 38081
- Auth service is running: `sudo systemctl status grump_auth.service`
- Port 38081 is listening: `sudo lsof -i :38081`
- Nginx reloaded: `sudo systemctl reload nginx`

### Cookie not working

**Check:**
- Using HTTPS (not HTTP) in production
- Nginx has `proxy_cookie_path / /grump/;`
- `AUTH_COOKIE_SECRET` is set in `.env`

## 📋 Quick Checklist

- [ ] Deployed files with `deploy_auth_to_production.sh`
- [ ] Created `.env` with real credentials
- [ ] Set `.env` permissions to 600
- [ ] Configured `allowed_people.txt`
- [ ] Updated Nginx config with proxy to port 38081
- [ ] Reloaded Nginx
- [ ] Started `grump_auth.service`
- [ ] Tested login flow end-to-end
- [ ] Verified emails are being sent
- [ ] Checked logs for errors

## 🔄 Update Procedure

When you need to update the auth system:

```bash
# 1. Upload new files to /home/graph/ftpbox/grump/

# 2. Copy updated files
sudo cp /home/graph/ftpbox/grump/auth_gate.py /var/www/grump-config/
sudo cp /home/graph/ftpbox/grump/login.html /var/www/iproot/grump/

# 3. Restart service
sudo systemctl restart grump_auth.service

# 4. Check status
sudo systemctl status grump_auth.service
```

## 📖 Documentation

- **Complete Setup:** `/home/graph/ftpbox/grump/AUTH_SETUP.md`
- **Quick Reference:** `/home/graph/ftpbox/grump/QUICK_AUTH_REFERENCE.md`
- **Implementation:** `/home/graph/ftpbox/grump/IMPLEMENTATION_SUMMARY.md`

## 🆘 Support

- Check logs: `sudo journalctl -u grump_auth.service -f`
- Test SMTP: Verify email sending works
- Review `.env`: Ensure all credentials are correct
- Contact: [@pdiomede on X](https://x.com/pdiomede)

---

**Port:** 38081 (auth gateway)  
**Service:** grump_auth.service  
**Config:** /var/www/grump-config/  
**Web:** /var/www/iproot/grump/

