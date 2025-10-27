#!/bin/bash
# Quick start script for The Graph Council Voting Monitor

# Change to script directory
cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found! Creating from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "Please edit wallets.txt with actual council member addresses before running."
    exit 1
fi

# Check if wallets.txt has real addresses
if grep -q "0x1234567890123456789012345678901234567890" wallets.txt; then
    echo "⚠️  Warning: wallets.txt still contains example addresses!"
    echo "Please update wallets.txt with real council member addresses."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if dependencies are installed
if ! python3 -c "import requests; import dotenv" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

# Run the monitor
echo "🚀 Running The Graph Council Voting Monitor..."
echo ""
python3 monitor_council_votes.py

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Report generated successfully!"
    echo "📄 Open index.html in your browser to view the report"
    
    # Try to open the HTML file automatically (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo ""
        read -p "Open report now? (Y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            open index.html
        fi
    fi
else
    echo ""
    echo "❌ An error occurred. Check the output above for details."
    exit 1
fi

