#!/bin/bash
#
# Deploy GOOSE Integration (v0.0.13) to Production
# This script deploys the new GOOSE dashboard files to production VPS
#

echo "============================================"
echo "🪿 THE GRUMPY GOOSE - Production Deployment"
echo "Version: v0.0.13"
echo "============================================"
echo ""

# Configuration
PROD_PATH="/var/www/iproot/grump"
SOURCE_PATH="$(cd "$(dirname "$0")" && pwd)"

echo "📂 Source Path: $SOURCE_PATH"
echo "📂 Production Path: $PROD_PATH"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run with sudo"
    echo "Usage: sudo bash $0"
    exit 1
fi

# Check if production directory exists
if [ ! -d "$PROD_PATH" ]; then
    echo "❌ Production directory does not exist: $PROD_PATH"
    exit 1
fi

echo "📋 Deploying files..."
echo ""

# Deploy new GOOSE files
echo "  → Copying goose.db..."
cp "$SOURCE_PATH/goose.db" "$PROD_PATH/" || { echo "❌ Failed to copy goose.db"; exit 1; }

echo "  → Copying council_members.csv..."
cp "$SOURCE_PATH/council_members.csv" "$PROD_PATH/" || { echo "❌ Failed to copy council_members.csv"; exit 1; }

echo "  → Copying goose_config.py..."
cp "$SOURCE_PATH/goose_config.py" "$PROD_PATH/" || { echo "❌ Failed to copy goose_config.py"; exit 1; }

echo "  → Copying goose_database.py..."
cp "$SOURCE_PATH/goose_database.py" "$PROD_PATH/" || { echo "❌ Failed to copy goose_database.py"; exit 1; }

echo "  → Copying goose_council.py..."
cp "$SOURCE_PATH/goose_council.py" "$PROD_PATH/" || { echo "❌ Failed to copy goose_council.py"; exit 1; }

echo "  → Copying goose_metrics.py..."
cp "$SOURCE_PATH/goose_metrics.py" "$PROD_PATH/" || { echo "❌ Failed to copy goose_metrics.py"; exit 1; }

echo "  → Copying updated monitor_council_votes.py..."
cp "$SOURCE_PATH/monitor_council_votes.py" "$PROD_PATH/" || { echo "❌ Failed to copy monitor_council_votes.py"; exit 1; }

echo ""
echo "🔒 Setting permissions..."

# Set ownership to www-data
chown -R www-data:www-data "$PROD_PATH/goose.db"
chown -R www-data:www-data "$PROD_PATH/council_members.csv"
chown -R www-data:www-data "$PROD_PATH/goose_*.py"
chown www-data:www-data "$PROD_PATH/monitor_council_votes.py"

# Set file permissions
chmod 644 "$PROD_PATH/goose.db"
chmod 644 "$PROD_PATH/council_members.csv"
chmod 644 "$PROD_PATH/goose_config.py"
chmod 644 "$PROD_PATH/goose_database.py"
chmod 644 "$PROD_PATH/goose_council.py"
chmod 644 "$PROD_PATH/goose_metrics.py"
chmod 644 "$PROD_PATH/monitor_council_votes.py"

echo ""
echo "🧪 Testing deployment..."
echo ""

# Test the script
cd "$PROD_PATH" || exit 1
sudo -u www-data python3 monitor_council_votes.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "📊 GOOSE Dashboard Features:"
    echo "   • Summary Cards (Proposals, Transactions, Votes, Members)"
    echo "   • Time to Quorum Statistics (All, Snapshot, Safe)"
    echo "   • Top 10 Member Leaderboard"
    echo "   • Member names displayed as 'Name (0xabc...xyz)'"
    echo ""
    echo "🌐 Check your dashboard at your VPS URL"
    echo ""
else
    echo ""
    echo "⚠️  Script ran but check for errors above"
    echo ""
fi

echo "============================================"
echo "Deployment Complete! 🎉"
echo "============================================"

