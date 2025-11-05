#!/bin/bash

# GRUMP Dashboard Authentication - Quick Setup Script
# ====================================================

echo "🔐 GRUMP Dashboard Authentication Setup"
echo "========================================"
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Setup cancelled. Keeping existing .env file."
        exit 0
    fi
fi

# Generate cookie secret
echo "🔑 Generating cookie secret..."
COOKIE_SECRET=$(python3 -c "import os; print(os.urandom(32).hex())")

# Get SMTP credentials
echo ""
echo "📧 Email Configuration"
echo "--------------------"
echo "This system needs to send OTP codes via email."
echo ""
read -p "SMTP Server (default: smtp.gmail.com): " SMTP_SERVER
SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}

read -p "SMTP Port (default: 587): " SMTP_PORT
SMTP_PORT=${SMTP_PORT:-587}

read -p "SMTP User (email address): " SMTP_USER
read -s -p "SMTP Password (App Password for Gmail): " SMTP_PASSWORD
echo ""

read -p "Email From (default: $SMTP_USER): " SMTP_FROM
SMTP_FROM=${SMTP_FROM:-$SMTP_USER}

read -p "Dashboard URL (default: http://localhost:38081/): " DASHBOARD_URL
DASHBOARD_URL=${DASHBOARD_URL:-http://localhost:38081/}

# Create .env file
echo ""
echo "📝 Creating .env file..."
cat > .env << EOF
# GRUMP Dashboard Authentication Configuration
# ============================================
# Generated on $(date)

# Authentication Cookie Secret
AUTH_COOKIE_SECRET=$COOKIE_SECRET

# SMTP Email Configuration
SMTP_SERVER=$SMTP_SERVER
SMTP_PORT=$SMTP_PORT
SMTP_USER=$SMTP_USER
SMTP_PASSWORD=$SMTP_PASSWORD
SMTP_FROM=$SMTP_FROM

# Dashboard URL
DASHBOARD_URL=$DASHBOARD_URL
EOF

# Set secure permissions
chmod 600 .env

echo ""
echo "✅ .env file created successfully!"
echo ""
echo "⚠️  IMPORTANT: Keep .env file secure - it contains sensitive credentials"
echo ""

# Check if allowed_people.txt exists
if [ ! -f "allowed_people.txt" ]; then
    echo "📋 Creating allowed_people.txt..."
    cp allowed_people.txt.example allowed_people.txt 2>/dev/null || cat > allowed_people.txt << EOF
# Email Whitelist for GRUMP Dashboard Access
# Add one email or pattern per line

# Authorized emails (remove # to activate):
*@thegraph.foundation
*@edgeandnode.com

# Add specific emails here:
# user@example.com
EOF
    echo "✅ allowed_people.txt created"
else
    echo "✅ allowed_people.txt already exists"
fi

# Create logs directory
mkdir -p logs
echo "✅ logs/ directory ready"

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Edit allowed_people.txt to add authorized email addresses"
echo "2. Run: python3 auth_gate.py"
echo "3. Visit: http://localhost:38081"
echo ""
echo "For Gmail users:"
echo "- Make sure you're using an App Password, not your regular password"
echo "- Get one at: https://myaccount.google.com/apppasswords"
echo ""
echo "For detailed instructions, see: AUTH_SETUP.md"
echo ""

