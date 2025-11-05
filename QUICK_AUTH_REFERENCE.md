# 🚀 Quick Authentication Reference

One-page reference for GRUMP Dashboard authentication.

## 📦 Files Added to Root

- `auth_gate.py` - Authentication server
- `login.html` - Login page UI
- `allowed_people.txt` - Email whitelist
- `.env.example` - Configuration template
- `auth_gate.service` - Systemd service file
- `setup_auth.sh` - Interactive setup script
- `test_auth_setup.py` - Verification script
- `AUTH_SETUP.md` - Complete setup guide
- `QUICK_AUTH_REFERENCE.md` - This file

## ⚡ Quick Start (3 Steps)

### 1. Configure Email
```bash
./setup_auth.sh
# Follow prompts to configure SMTP
```

### 2. Edit Whitelist
```bash
nano allowed_people.txt
# Uncomment authorized emails
```

### 3. Start Server
```bash
python3 auth_gate.py
# Visit: http://localhost:38081
```

## 🔧 Manual Setup

```bash
# Copy environment template
cp .env.example .env

# Generate cookie secret
python3 -c "import os; print(os.urandom(32).hex())"

# Edit .env with your SMTP credentials
nano .env

# Edit whitelist
nano allowed_people.txt

# Test setup
./test_auth_setup.py

# Start server
python3 auth_gate.py
# Opens on: http://localhost:38081
```

## 📧 Gmail Setup

1. Enable 2FA: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Use 16-char password in `.env`

```env
AUTH_COOKIE_SECRET=<generated-secret>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
DASHBOARD_URL=http://localhost:38081/
```

## 👥 Whitelist Examples

```txt
# Allow specific users
yaniv@edgeandnode.com
admin@example.com

# Allow entire domains
*@thegraph.foundation
*@edgeandnode.com
```

## 🔍 Testing

```bash
# Verify setup
./test_auth_setup.py

# Test manually
python3 auth_gate.py
# Then open: http://localhost:38081
```

## 📊 Common Commands

| Command | Purpose |
|---------|---------|
| `./setup_auth.sh` | Interactive setup |
| `./test_auth_setup.py` | Verify configuration |
| `python3 auth_gate.py` | Start auth server |
| `nano allowed_people.txt` | Edit whitelist |
| `nano .env` | Edit config |

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Email not sending | Check SMTP credentials, use App Password for Gmail |
| Email not authorized | Add to `allowed_people.txt` |
| Connection error | Check server is running on port 38081 |
| Cookie not working | Verify `AUTH_COOKIE_SECRET` is set |

## 🔐 How It Works

```
User visits http://localhost:38081
    ↓
Check session cookie
    ↓
┌─────────┬─────────┐
No cookie    Valid cookie
    ↓           ↓
Login page   Dashboard
    ↓
Enter email
    ↓
Send OTP code
    ↓
Enter code
    ↓
Create session
    ↓
Dashboard
```

## 📁 File Structure

```
grump/
├── auth_gate.py          # Auth server
├── login.html            # Login UI
├── index.html            # Dashboard
├── allowed_people.txt    # Whitelist
├── .env                  # Config (SECRET!)
├── setup_auth.sh         # Setup script
├── test_auth_setup.py    # Test script
└── logs/                 # Log directory
```

## 🎯 URLs

- **Development:** http://localhost:38081
- **Production:** https://dashboards.thegraph.foundation/grump/

## 📚 Documentation

- **Complete Guide:** [AUTH_SETUP.md](AUTH_SETUP.md)
- **Production Deploy:** `auth/README.md`
- **Quick Start:** `auth/QUICKSTART_AUTH.md`
- **Nginx Config:** `auth/NGINX_MODIFICATION_GUIDE.md`

## 🔒 Security Checklist

- [ ] Strong `AUTH_COOKIE_SECRET` (64+ chars)
- [ ] Gmail App Password (not regular password)
- [ ] `.env` file is in `.gitignore`
- [ ] Whitelist configured with authorized emails
- [ ] SMTP credentials tested
- [ ] Login flow tested end-to-end

## 💡 Tips

- **Whitelist changes** take effect immediately (no restart)
- **Session cookies** last 7 days
- **OTP codes** expire in 10 minutes
- **Rate limit** is 5 OTP requests per hour per email
- **Logs** show all authentication events

## 🆘 Help

- Review: [AUTH_SETUP.md](AUTH_SETUP.md)
- Check logs: `tail -f logs/auth_gateway.log`
- Test SMTP: `./test_auth_setup.py`
- Contact: [@pdiomede on X](https://x.com/pdiomede)

---

**Quick Links:**
- [Full Setup Guide](AUTH_SETUP.md)
- [Main README](README.md)
- [Production Docs](auth/README.md)

