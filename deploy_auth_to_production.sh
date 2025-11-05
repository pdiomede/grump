#!/bin/bash

# GRUMP Authentication - Production Deployment Script
# ====================================================
# This script deploys the authentication system from the upload directory
# to the production directories on your VPS.
#
# Source directory: /home/graph/ftpbox/grump/
# Target directories:
#   - Config: /var/www/grump-config/
#   - Web: /var/www/iproot/grump/

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║           🔐 GRUMP Authentication - Production Deployment                  ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
SOURCE_DIR="/home/graph/ftpbox/grump"
CONFIG_DIR="/var/www/grump-config"
WEB_DIR="/var/www/iproot/grump"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
   echo "❌ This script must be run with sudo privileges"
   echo "   Please run: sudo bash deploy_auth_to_production.sh"
   exit 1
fi

echo "📁 Source Directory: $SOURCE_DIR"
echo "📁 Config Directory: $CONFIG_DIR"
echo "📁 Web Directory: $WEB_DIR"
echo ""

# Verify source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Source directory not found: $SOURCE_DIR"
    echo "   Please upload files to this directory first"
    exit 1
fi

echo "✅ Source directory found"
echo ""

# ============================================================================
# Step 1: Create Directories
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 1: Creating directories"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

mkdir -p "$CONFIG_DIR"
mkdir -p "$WEB_DIR/logs"

echo "✅ Directories created:"
echo "   - $CONFIG_DIR"
echo "   - $WEB_DIR/logs"
echo ""

# ============================================================================
# Step 2: Copy Config Files
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 2: Copying config files to $CONFIG_DIR"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Copy auth_gate.py
if [ -f "$SOURCE_DIR/auth_gate.py" ]; then
    cp "$SOURCE_DIR/auth_gate.py" "$CONFIG_DIR/"
    echo "✅ Copied: auth_gate.py"
else
    echo "⚠️  Not found: auth_gate.py"
fi

# Copy allowed_people.txt (or create from example)
if [ -f "$SOURCE_DIR/allowed_people.txt" ]; then
    cp "$SOURCE_DIR/allowed_people.txt" "$CONFIG_DIR/"
    echo "✅ Copied: allowed_people.txt"
elif [ -f "$SOURCE_DIR/allowed_people.txt.example" ]; then
    cp "$SOURCE_DIR/allowed_people.txt.example" "$CONFIG_DIR/allowed_people.txt"
    echo "✅ Created: allowed_people.txt (from example)"
else
    echo "⚠️  Not found: allowed_people.txt"
fi

# Copy .env.example (DO NOT copy actual .env if it exists - contains secrets)
if [ -f "$SOURCE_DIR/.env.example" ]; then
    cp "$SOURCE_DIR/.env.example" "$CONFIG_DIR/"
    echo "✅ Copied: .env.example"
fi

echo ""
echo "⚠️  IMPORTANT: You need to create .env file with your credentials"
echo "   Template is at: $CONFIG_DIR/.env.example"
echo ""

# ============================================================================
# Step 3: Copy Web Files
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 3: Copying web files to $WEB_DIR"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Copy login.html
if [ -f "$SOURCE_DIR/login.html" ]; then
    cp "$SOURCE_DIR/login.html" "$WEB_DIR/"
    echo "✅ Copied: login.html"
else
    echo "⚠️  Not found: login.html"
fi

# Verify index.html exists (your dashboard)
if [ -f "$WEB_DIR/index.html" ]; then
    echo "✅ Found: index.html (existing dashboard)"
else
    echo "⚠️  index.html not found in $WEB_DIR"
    echo "   Make sure your dashboard is generated first"
fi

# Copy other dashboard files if they exist in source
if [ -f "$SOURCE_DIR/monitor_council_votes.py" ]; then
    cp "$SOURCE_DIR/monitor_council_votes.py" "$WEB_DIR/"
    echo "✅ Copied: monitor_council_votes.py"
fi

if [ -f "$SOURCE_DIR/wallets.txt" ]; then
    cp "$SOURCE_DIR/wallets.txt" "$WEB_DIR/"
    echo "✅ Copied: wallets.txt"
fi

echo ""

# ============================================================================
# Step 4: Set Permissions
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 4: Setting permissions"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Set ownership to www-data
chown -R www-data:www-data "$CONFIG_DIR"
chown -R www-data:www-data "$WEB_DIR"

# Set file permissions
chmod 644 "$CONFIG_DIR/auth_gate.py"
chmod 644 "$CONFIG_DIR/allowed_people.txt"
chmod 644 "$WEB_DIR/login.html"

# Set directory permissions
chmod 755 "$CONFIG_DIR"
chmod 755 "$WEB_DIR"
chmod 755 "$WEB_DIR/logs"

echo "✅ Permissions set:"
echo "   - Owner: www-data:www-data"
echo "   - Files: 644"
echo "   - Directories: 755"
echo ""

# ============================================================================
# Step 5: Install Systemd Service
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 5: Installing systemd service"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

if [ -f "$SOURCE_DIR/auth_gate.service" ]; then
    cp "$SOURCE_DIR/auth_gate.service" /etc/systemd/system/grump_auth.service
    systemctl daemon-reload
    echo "✅ Systemd service installed: grump_auth.service"
else
    echo "⚠️  auth_gate.service not found, creating it..."
    cat > /etc/systemd/system/grump_auth.service << 'EOF'
[Unit]
Description=GRUMP Dashboard Authentication Gateway
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/grump-config
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /var/www/grump-config/auth_gate.py
Restart=always
RestartSec=10
StandardOutput=append:/var/www/iproot/grump/logs/auth_gateway.log
StandardError=append:/var/www/iproot/grump/logs/auth_gateway.log

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/iproot/grump/logs
ReadOnlyPaths=/var/www/grump-config

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    echo "✅ Created and installed: grump_auth.service"
fi

echo ""

# ============================================================================
# Step 6: Install Python Dependencies
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 6: Installing Python dependencies"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

pip3 install bottle python-dotenv

echo "✅ Python dependencies installed"
echo ""

# ============================================================================
# SUMMARY & NEXT STEPS
# ============================================================================
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║                        ✅ DEPLOYMENT COMPLETE!                             ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Files deployed to:"
echo "   • Config: $CONFIG_DIR"
echo "   • Web: $WEB_DIR"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "🚨 REQUIRED NEXT STEPS (MANUAL)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  CREATE .env FILE WITH YOUR CREDENTIALS:"
echo "   -------------------------------------------"
echo "   sudo nano $CONFIG_DIR/.env"
echo ""
echo "   Add this content (replace with your real values):"
echo "   -------------------------------------------------"
echo "   # Generate cookie secret with:"
echo "   # python3 -c \"import os; print(os.urandom(32).hex())\""
echo "   AUTH_COOKIE_SECRET=<paste-generated-64-char-secret>"
echo ""
echo "   # Gmail SMTP (use App Password, not regular password)"
echo "   # Get App Password: https://myaccount.google.com/apppasswords"
echo "   SMTP_SERVER=smtp.gmail.com"
echo "   SMTP_PORT=587"
echo "   SMTP_USER=your-email@gmail.com"
echo "   SMTP_PASSWORD=your-16-char-app-password"
echo "   SMTP_FROM=your-email@gmail.com"
echo ""
echo "   # Production URL"
echo "   DASHBOARD_URL=https://dashboards.thegraph.foundation/grump/"
echo ""
echo "   Then set secure permissions:"
echo "   sudo chmod 600 $CONFIG_DIR/.env"
echo "   sudo chown www-data:www-data $CONFIG_DIR/.env"
echo ""
echo "2️⃣  CONFIGURE EMAIL WHITELIST:"
echo "   ---------------------------"
echo "   sudo nano $CONFIG_DIR/allowed_people.txt"
echo ""
echo "   Add authorized emails (one per line):"
echo "   *@thegraph.foundation"
echo "   *@edgeandnode.com"
echo "   user@example.com"
echo ""
echo "3️⃣  CONFIGURE NGINX (IF NOT ALREADY DONE):"
echo "   ----------------------------------------"
echo "   Edit your Nginx config:"
echo "   sudo nano /etc/nginx/sites-available/dashboards.thegraph.foundation.conf"
echo ""
echo "   Add/update the /grump/ location block:"
echo "   ---------------------------------------"
echo "   location /grump/ {"
echo "       # Proxy to auth gateway (port 38081)"
echo "       proxy_pass http://127.0.0.1:38081/;"
echo "       proxy_set_header Host \$host;"
echo "       proxy_set_header X-Real-IP \$remote_addr;"
echo "       proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
echo "       proxy_set_header X-Forwarded-Proto \$scheme;"
echo "       proxy_cookie_path / /grump/;"
echo "   }"
echo ""
echo "   Test and reload Nginx:"
echo "   sudo nginx -t"
echo "   sudo systemctl reload nginx"
echo ""
echo "4️⃣  START THE AUTHENTICATION SERVICE:"
echo "   -----------------------------------"
echo "   sudo systemctl enable grump_auth.service"
echo "   sudo systemctl start grump_auth.service"
echo "   sudo systemctl status grump_auth.service"
echo ""
echo "5️⃣  VERIFY LOGS:"
echo "   -------------"
echo "   # View service logs"
echo "   sudo journalctl -u grump_auth.service -f"
echo ""
echo "   # Or view log file"
echo "   tail -f $WEB_DIR/logs/auth_gateway.log"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "📝 QUICK TEST (BEFORE CONFIGURING .env)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "# Test the auth gateway manually (will warn about missing .env):"
echo "sudo -u www-data python3 $CONFIG_DIR/auth_gate.py"
echo ""
echo "# Press Ctrl+C to stop"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "🔍 VERIFICATION CHECKLIST"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "[ ] .env file created with real credentials"
echo "[ ] .env file has 600 permissions (sudo chmod 600)"
echo "[ ] allowed_people.txt configured with authorized emails"
echo "[ ] Nginx configured to proxy /grump/ to port 38081"
echo "[ ] Nginx reloaded successfully"
echo "[ ] grump_auth.service started"
echo "[ ] Can access: https://dashboards.thegraph.foundation/grump/"
echo "[ ] Login page appears"
echo "[ ] Can send OTP code to authorized email"
echo "[ ] Can login with OTP code"
echo "[ ] Dashboard loads after login"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "🆘 TROUBLESHOOTING"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "# Check service status:"
echo "sudo systemctl status grump_auth.service"
echo ""
echo "# View recent logs:"
echo "sudo journalctl -u grump_auth.service -n 50"
echo ""
echo "# Check if port 38081 is listening:"
echo "sudo lsof -i :38081"
echo ""
echo "# Restart service:"
echo "sudo systemctl restart grump_auth.service"
echo ""
echo "# Test SMTP connection:"
echo "python3 -c \"import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls()\""
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "📖 For detailed documentation, see:"
echo "   - $SOURCE_DIR/AUTH_SETUP.md"
echo "   - $SOURCE_DIR/QUICK_AUTH_REFERENCE.md"
echo ""
echo "✅ Deployment script completed!"
echo ""

