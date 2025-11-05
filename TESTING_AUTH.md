# 🧪 Authentication System Testing Guide

Complete guide for testing the authentication system locally and in production.

## 🏠 LOCAL TESTING (Before VPS Deployment)

### Prerequisites

- [ ] Python 3.7+ installed
- [ ] Files in local directory
- [ ] Gmail account with 2FA enabled
- [ ] Gmail App Password created

### Step 1: Install Dependencies

```bash
cd /Users/pdiomede/Documents/WORK/_coding/controldeck/grump
pip3 install -r requirements.txt
```

Should install:
- `bottle>=0.12.25`
- `python-dotenv>=1.0.0`
- `requests` (for dashboard)

### Step 2: Configure SMTP (Email)

**Option A: Interactive Setup (Recommended)**
```bash
./setup_auth.sh
```

**Option B: Manual Setup**
```bash
# Generate cookie secret
python3 -c "import os; print(os.urandom(32).hex())"

# Create .env file
nano .env
```

Add this content:
```env
AUTH_COOKIE_SECRET=<paste-64-char-secret-from-above>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM=your-email@gmail.com
DASHBOARD_URL=http://localhost:38081/
```

**Get Gmail App Password:**
1. Enable 2FA: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Select "Mail" and generate
4. Copy the 16-character password

### Step 3: Configure Whitelist

```bash
nano allowed_people.txt
```

Add your email for testing:
```
*@thegraph.foundation
*@edgeandnode.com
your-test-email@gmail.com
```

### Step 4: Verify Configuration

```bash
./test_auth_setup.py
```

Expected output:
```
🔐 GRUMP Authentication Setup Verification
============================================================

📁 Checking Required Files...
✅ Authentication gateway: auth_gate.py
✅ Login page: login.html
✅ Email whitelist: allowed_people.txt
✅ Environment configuration: .env
✅ Dashboard: index.html

📂 Checking Directories...
✅ Logs directory: logs

🔧 Checking Environment Variables...
✅ AUTH_COOKIE_SECRET: ********
✅ SMTP_SERVER: smtp.gmail.com
✅ SMTP_PORT: 587
✅ SMTP_USER: your-email@gmail.com
✅ SMTP_PASSWORD: ********

👥 Checking Whitelist Configuration...
✅ Whitelist configured with 3 entries

📧 Testing Email Configuration...
🔌 Testing SMTP connection to smtp.gmail.com:587...
✅ SMTP connection successful!

============================================================
📊 Summary
============================================================
🎉 All checks passed! Authentication system is ready.

Next steps:
1. Run: python3 auth_gate.py
2. Visit: http://localhost:38081
3. Login with an authorized email
```

### Step 5: Generate Dashboard

```bash
# Make sure your dashboard exists
python3 monitor_council_votes.py
```

This creates `index.html` which the auth system will protect.

### Step 6: Start Auth Server

```bash
python3 auth_gate.py
```

Expected output:
```
============================================================
🔐 GRUMP Dashboard Authentication Gateway
============================================================
⚠️  WARNING: SMTP credentials not configured!   (if not configured)
   Set SMTP_USER and SMTP_PASSWORD in .env file

📧 Loaded 3 email patterns from whitelist

✅ Found: index.html (existing dashboard)
✅ Found: login.html (login page)

🔧 Running in DEVELOPMENT mode from: /path/to/grump
   For production, deploy to: /var/www/grump-config

🚀 Starting server...
   URL: http://localhost:38081
   Cookie expiry: 7 days
   OTP expiry: 10 minutes

Press Ctrl+C to stop
============================================================
```

**Keep this terminal open!** The server is now running.

### Step 7: Test Login Flow

Open a new terminal or browser:

**1. Visit Login Page**
```
Open: http://localhost:38081
```

✅ **Expected:** You should see a beautiful purple login page with:
- 🔐 Logo
- "GRUMP Dashboard" title
- Email input field
- "Request Login Code" button

**2. Enter Email**
- Type an authorized email (from allowed_people.txt)
- Click "Request Login Code"

✅ **Expected:** 
- Success message: "Check your email for the login code"
- Form changes to show OTP input field

**3. Check Email**
- Open your email inbox
- Look for email with subject: "Your GRUMP Dashboard Login Code"

✅ **Expected Email Content:**
```
GRUMP Dashboard - One-Time Password

Your login code is: 123456

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.
```

**4. Enter OTP Code**
- Copy the 6-digit code from email
- Paste into the OTP input field
- Click "Verify Code"

✅ **Expected:**
- Success message: "Login successful! Redirecting..."
- Page refreshes automatically
- You see your dashboard (index.html)

**5. Verify Session**
- Close the browser
- Open again and visit: http://localhost:38081

✅ **Expected:** 
- You're still logged in (no login page)
- Dashboard loads immediately
- Session lasts 7 days

**6. Test Logout**
- Visit: http://localhost:38081/logout

✅ **Expected:**
- Redirected to login page
- Session cleared
- Must login again to access dashboard

### Step 8: Check Logs

In the terminal where `auth_gate.py` is running, you should see:

```
✅ [2025-11-05 10:30:45 UTC] OTP_SENT: user@example.com - Code: 123456
✅ [2025-11-05 10:32:18 UTC] LOGIN_SUCCESS: user@example.com - Session created
```

### Step 9: Test Error Cases

**Test 1: Unauthorized Email**
- Try to login with email not in whitelist
- ✅ Expected: "Email not authorized. Please contact an administrator."

**Test 2: Wrong OTP Code**
- Request OTP
- Enter wrong code
- ✅ Expected: "Invalid code. Please try again."

**Test 3: Expired OTP**
- Request OTP
- Wait 11 minutes
- Enter code
- ✅ Expected: "Code expired. Please request a new one."

**Test 4: Rate Limiting**
- Request OTP 6 times in a row
- ✅ Expected: "Too many requests. Please try again later."

---

## 🌐 PRODUCTION TESTING (After VPS Deployment)

### Prerequisites

- [ ] Files deployed to VPS
- [ ] Deployment script ran successfully
- [ ] `.env` file created on VPS
- [ ] `allowed_people.txt` configured
- [ ] Nginx configured
- [ ] Service started

### Step 1: Verify Service is Running

```bash
# SSH into your VPS
ssh your-vps

# Check service status
sudo systemctl status grump_auth.service
```

✅ **Expected Output:**
```
● grump_auth.service - GRUMP Dashboard Authentication Gateway
     Loaded: loaded (/etc/systemd/system/grump_auth.service; enabled)
     Active: active (running) since Wed 2025-11-05 10:00:00 UTC
```

If not running:
```bash
sudo systemctl start grump_auth.service
sudo systemctl status grump_auth.service
```

### Step 2: Check Logs

```bash
# View real-time logs
sudo journalctl -u grump_auth.service -f

# Or view log file
tail -f /var/www/iproot/grump/logs/auth_gateway.log
```

✅ **Expected Output:**
```
============================================================
🔐 GRUMP Dashboard Authentication Gateway
============================================================
📧 Loaded X email patterns from whitelist
🚀 Starting server...
   URL: http://localhost:38081
   ...
```

### Step 3: Verify Port is Listening

```bash
sudo lsof -i :38081
```

✅ **Expected Output:**
```
COMMAND    PID     USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3  12345 www-data    3u  IPv4  67890      0t0  TCP *:38081 (LISTEN)
```

### Step 4: Test Nginx Proxy

```bash
# Check nginx config
sudo nginx -t

# View nginx config
sudo cat /etc/nginx/sites-available/dashboards.thegraph.foundation.conf | grep -A 10 "location /grump"
```

✅ **Expected:** Should show proxy_pass to `http://127.0.0.1:38081/`

### Step 5: Test from Browser

**1. Visit Dashboard URL**
```
https://dashboards.thegraph.foundation/grump/
```

✅ **Expected:** Login page appears (not dashboard)

**2. Complete Login Flow**
- Enter authorized email
- Check email for OTP
- Enter OTP code
- Should see dashboard

**3. Test Session Persistence**
- Close browser
- Reopen and visit same URL
- ✅ Should still be logged in (no login page)

**4. Test Logout**
```
https://dashboards.thegraph.foundation/grump/logout
```
✅ Should redirect to login page

### Step 6: Monitor Logs During Test

In SSH session, run:
```bash
sudo journalctl -u grump_auth.service -f
```

During login, you should see:
```
✅ [timestamp] OTP_SENT: user@example.com - Code: 123456
✅ [timestamp] LOGIN_SUCCESS: user@example.com - Session created
```

### Step 7: Test from Multiple Devices

- Test from desktop browser
- Test from mobile browser
- Test from incognito/private mode

All should work correctly.

---

## 🐛 Troubleshooting

### Issue: Server Won't Start

**Check logs:**
```bash
sudo journalctl -u grump_auth.service -n 50
```

**Common causes:**
- `.env` file missing
- Invalid Python syntax
- Port 38081 already in use
- Missing dependencies

**Solution:**
```bash
# Test manually
sudo -u www-data python3 /var/www/grump-config/auth_gate.py
```

### Issue: Email Not Sending

**Test SMTP connection:**
```bash
python3 << 'EOF'
import smtplib
from dotenv import load_dotenv
import os

load_dotenv('/var/www/grump-config/.env')

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
print("✅ SMTP connection successful!")
server.quit()
EOF
```

**Common causes:**
- Using regular password (not App Password)
- Wrong credentials in `.env`
- Firewall blocking port 587
- 2FA not enabled on Gmail

### Issue: 404 Not Found

**Check:**
- Nginx proxy configured correctly
- Service is running
- Port 38081 is listening
- Nginx has been reloaded

```bash
sudo systemctl reload nginx
```

### Issue: Login Page Loads but Dashboard Doesn't

**Check:**
- `index.html` exists in `/var/www/iproot/grump/`
- Run dashboard generator: `python3 /var/www/iproot/grump/monitor_council_votes.py`
- Check file permissions

### Issue: Cookie Not Working

**Check:**
- Using HTTPS (not HTTP) in production
- `AUTH_COOKIE_SECRET` is set in `.env`
- Nginx has `proxy_cookie_path / /grump/;`
- Clear browser cookies and try again

---

## ✅ Testing Checklist

### Local Testing
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Whitelist configured
- [ ] `test_auth_setup.py` passes all checks
- [ ] Server starts without errors
- [ ] Login page loads at http://localhost:38081
- [ ] Can request OTP code
- [ ] Receive OTP email
- [ ] Can login with OTP
- [ ] Dashboard loads after login
- [ ] Session persists after browser restart
- [ ] Logout works correctly
- [ ] Logs show auth events

### Production Testing
- [ ] Service is running
- [ ] Port 38081 is listening
- [ ] Nginx proxy configured
- [ ] HTTPS works correctly
- [ ] Login page loads at production URL
- [ ] Can request OTP code
- [ ] Receive OTP email
- [ ] Can login with OTP
- [ ] Dashboard loads after login
- [ ] Session persists across devices
- [ ] Logout works correctly
- [ ] Logs show auth events
- [ ] Tested from multiple browsers
- [ ] Tested from mobile device

---

## 📊 Performance Testing

### Test Rate Limiting

```bash
# Send 6 OTP requests rapidly
for i in {1..6}; do
  curl -X POST http://localhost:38081/request-otp \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com"}'
  echo ""
done
```

✅ **Expected:** 6th request should fail with rate limit message

### Test Session Duration

- Login
- Check cookie expiry in browser dev tools
- ✅ Should be 7 days from login time

### Test Concurrent Users

- Login from 3 different browsers simultaneously
- ✅ All should work independently

---

## 🎯 Success Criteria

Your authentication is working correctly when:

- ✅ Login page appears for unauthenticated users
- ✅ Dashboard appears for authenticated users
- ✅ OTP codes are sent via email within seconds
- ✅ OTP codes work and expire after 10 minutes
- ✅ Sessions last 7 days
- ✅ Logout clears session
- ✅ Rate limiting prevents abuse
- ✅ Unauthorized emails are rejected
- ✅ All events are logged
- ✅ System works on HTTPS in production

---

## 📖 Quick Commands Reference

### Local Testing
```bash
# Setup
./setup_auth.sh                    # Configure
./test_auth_setup.py              # Verify

# Run
python3 auth_gate.py              # Start server

# Test
open http://localhost:38081       # Open in browser
```

### Production Testing
```bash
# Status
sudo systemctl status grump_auth.service

# Logs
sudo journalctl -u grump_auth.service -f
tail -f /var/www/iproot/grump/logs/auth_gateway.log

# Verify
sudo lsof -i :38081               # Check port
curl -I https://dashboards.thegraph.foundation/grump/  # Test URL

# Control
sudo systemctl restart grump_auth.service   # Restart
sudo systemctl stop grump_auth.service      # Stop
sudo systemctl start grump_auth.service     # Start
```

---

**Ready to test!** Start with local testing, then move to production. 🧪

