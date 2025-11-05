# 🔐 GRUMP Dashboard Authentication Setup

Complete guide to set up email-based OTP authentication for the GRUMP Dashboard.

## 📋 Overview

The authentication system has been moved to the root directory and configured to work in both development and production modes. It uses:

- **Email-based OTP** (One-Time Password) authentication
- **Whitelist system** to control access
- **7-day session cookies** for persistent login
- **Rate limiting** to prevent abuse
- **Audit logging** of all authentication events

## 🚀 Quick Start (Local Development)

### Step 1: Configure Email (REQUIRED)

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Then edit `.env` with your email credentials:

```bash
# Generate a cookie secret (run this command):
python3 -c "import os; print(os.urandom(32).hex())"

# Edit .env and add:
AUTH_COOKIE_SECRET=<paste-generated-secret-here>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM=your-email@gmail.com
DASHBOARD_URL=http://localhost:38081/
```

#### Getting Gmail App Password:

1. Enable **2-Factor Authentication** on your Google account
2. Visit: https://myaccount.google.com/apppasswords
3. Create an App Password for "Mail"
4. Use the 16-character password as `SMTP_PASSWORD` in `.env`

**Important:** You must use an App Password, not your regular Gmail password!

### Step 2: Configure Authorized Users

Edit `allowed_people.txt` to add authorized email addresses:

```bash
# Uncomment the domains/emails you want to allow:
*@thegraph.foundation
*@edgeandnode.com

# Or add specific emails:
user@example.com
admin@company.com
```

**Supports:**
- Exact emails: `user@example.com`
- Wildcard domains: `*@thegraph.foundation` (allows all emails from that domain)

### Step 3: Start the Authentication Gateway

```bash
python3 auth_gate.py
```

The server will start on http://localhost:38081

You should see:
```
🔧 Running in DEVELOPMENT mode from: /path/to/grump
📧 Loaded 2 email patterns from whitelist
🚀 Starting server...
   URL: http://localhost:38081
```

### Step 4: Test the Login Flow

1. Open http://localhost:38081 in your browser
2. You'll see the **login page** (login.html)
3. Enter an authorized email address
4. Check your email for the 6-digit OTP code
5. Enter the code to login
6. You'll be redirected to the **dashboard** (index.html)

## 📂 File Structure

After setup, you should have:

```
/grump/
├── auth_gate.py              # Authentication gateway server
├── login.html                # Login page UI
├── index.html                # Your dashboard (existing)
├── allowed_people.txt        # Email whitelist
├── .env                      # Environment variables (SECRET!)
├── .env.example              # Environment template
├── logs/                     # Log directory
│   └── auth_gateway.log      # Auth logs (created on first run)
├── monitor_council_votes.py  # Your existing dashboard script
└── ...other files
```

## 🔧 Configuration Options

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `AUTH_COOKIE_SECRET` | Secret key for signing cookies | `3a2590b94dc...` (64 chars) |
| `SMTP_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP password/app password | `abcd efgh ijkl mnop` |
| `SMTP_FROM` | Email sender address | `your-email@gmail.com` |
| `DASHBOARD_URL` | Dashboard URL for email links | `http://localhost:38081/` |

### Whitelist Configuration (allowed_people.txt)

- One email/pattern per line
- Lines starting with `#` are comments
- Empty lines are ignored
- Changes take effect immediately (no restart needed)

**Examples:**
```
# Allow specific users
yaniv@edgeandnode.com
admin@example.com

# Allow entire domains
*@thegraph.foundation
*@edgeandnode.com
```

## 🔐 Security Features

- ✅ **Email whitelist** - Only authorized emails can access
- ✅ **OTP codes** - 6-digit codes expire in 10 minutes
- ✅ **Signed cookies** - Tamper-proof session cookies
- ✅ **7-day sessions** - Stay logged in for a week
- ✅ **Rate limiting** - Max 5 OTP requests per hour per email
- ✅ **Audit logging** - All auth events are logged
- ✅ **HTTPS support** - Secure cookies in production

## 📊 Monitoring

### View Logs

```bash
# If running in foreground
# Logs appear in terminal

# If running as background service
tail -f logs/auth_gateway.log
```

### Log Examples

**Successful login:**
```
✅ [2025-11-05 10:30:45 UTC] OTP_SENT: user@example.com - Code: 123456
✅ [2025-11-05 10:32:18 UTC] LOGIN_SUCCESS: user@example.com - Session created
```

**Failed attempts:**
```
❌ [2025-11-05 10:45:23 UTC] OTP_REQUEST: hacker@bad.com - Email not whitelisted
❌ [2025-11-05 11:22:09 UTC] OTP_VERIFY: user@example.com - Invalid code
```

## 🐛 Troubleshooting

### Issue: Email not sending

**Solutions:**
- Verify SMTP credentials in `.env`
- For Gmail: ensure using App Password, not regular password
- Test SMTP connection:
  ```bash
  python3 -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls()"
  ```

### Issue: "Email not authorized"

**Solutions:**
- Add email to `allowed_people.txt`
- Check for typos in email address
- Verify file format (one email per line)

### Issue: "Connection error"

**Solutions:**
- Check if auth_gate.py is running
- Verify port 38081 is not in use:
  ```bash
  lsof -i :38081
  ```

### Issue: Cookie not working

**Solutions:**
- Ensure `AUTH_COOKIE_SECRET` is set in `.env`
- For production, use HTTPS (HTTP cookies work in development)
- Clear browser cookies and try again

## 🌐 Alternative SMTP Providers

### SendGrid

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
```

### AWS SES

```bash
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your_ses_smtp_username
SMTP_PASSWORD=your_ses_smtp_password
```

### Mailgun

```bash
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your_mailgun_smtp_password
```

## 🚀 Production Deployment

For production deployment to `/var/www/`, see the detailed guides in the `auth/` directory:

- `auth/QUICKSTART_AUTH.md` - Quick production setup
- `auth/README.md` - Complete production documentation
- `auth/NGINX_MODIFICATION_GUIDE.md` - Nginx configuration
- `auth/SETUP_STEPS.md` - Detailed setup steps

The `auth_gate.py` script automatically detects the environment:
- **Development mode** - Uses current directory if `/var/www/grump-config/` doesn't exist
- **Production mode** - Uses `/var/www/grump-config/` and `/var/www/iproot/grump/` if they exist

## 📝 Management Commands

### Update Whitelist

```bash
nano allowed_people.txt
# Changes take effect immediately - no restart needed
```

### Rotate Cookie Secret (logs out all users)

```bash
# Generate new secret
python3 -c "import os; print(os.urandom(32).hex())"

# Update .env with new secret
nano .env

# Restart auth_gate.py
# (kill and restart the process)
```

### Check Server Status

```bash
# If running in terminal - just check terminal
# If running as background process:
ps aux | grep auth_gate.py
```

## 🎉 Features

### User Experience
- 🎨 Beautiful, modern login UI
- 📧 HTML-formatted OTP emails
- 📱 Mobile-friendly design
- ⚡ Fast in-memory storage
- 🔄 Auto-redirect after login

### Developer Experience
- 🔧 Works in both dev and production
- 📝 Comprehensive logging
- 🔍 Easy debugging
- 📦 Simple setup (3 files)
- 🛠️ No database required

## 🔗 Integration

The authentication system acts as a **gateway** to your existing dashboard:

- **Your existing `index.html`** - No changes needed! ✅
- **Your existing `monitor_council_votes.py`** - No changes needed! ✅
- **Your existing data files** - No changes needed! ✅

The auth gateway:
1. Intercepts all requests
2. Shows login page if not authenticated
3. Shows dashboard if authenticated
4. Serves all static files (images, CSS, JS)

## 📚 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. User visits http://localhost:38081                     │
│     ↓                                                       │
│  2. auth_gate.py checks for valid session cookie           │
│     ↓                                                       │
│  3a. NO COOKIE → Show login.html                           │
│     ↓                                                       │
│  4. User enters email → Request OTP                        │
│     ↓                                                       │
│  5. Check whitelist → Send OTP via email                   │
│     ↓                                                       │
│  6. User enters OTP → Verify code                          │
│     ↓                                                       │
│  7. Set session cookie (7 days)                            │
│     ↓                                                       │
│  3b. VALID COOKIE → Show index.html (dashboard)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🆘 Getting Help

1. **Check logs** - Look for error messages in terminal or `logs/auth_gateway.log`
2. **Test SMTP** - Verify email sending works separately
3. **Check whitelist** - Ensure your email is authorized
4. **Review .env** - Verify all credentials are correct

## ✅ Quick Checklist

Before going live:

- [ ] `.env` file created with real SMTP credentials
- [ ] `AUTH_COOKIE_SECRET` is a strong random string (64 chars)
- [ ] Gmail App Password configured (if using Gmail)
- [ ] `allowed_people.txt` has authorized emails
- [ ] `logs/` directory exists
- [ ] Tested login flow end-to-end
- [ ] Can send emails successfully
- [ ] Dashboard loads after authentication

## 📮 Support

For issues or questions:
- Check the documentation in `auth/` directory
- Review logs for error messages
- Contact [@pdiomede on X](https://x.com/pdiomede)

---

**Version:** 1.0.0  
**Last Updated:** November 5, 2025  
**Author:** [@pdiomede](https://x.com/pdiomede)  
**License:** MIT

