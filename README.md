# The Graph Council Voting Monitor

A Python-based monitoring tool that tracks voting activity on The Graph Council's governance proposals via Snapshot and alerts when council members haven't voted after a configurable threshold (default: 5 days).

## 🎯 Purpose

The Graph Council consists of 6 members who vote on Graph Governance Proposals (GGPs) posted on https://snapshot.org/#/council.graphprotocol.eth. This tool helps ensure full participation by:

- Monitoring active proposals on Snapshot
- Tracking which council members have/haven't voted
- Generating alerts when members haven't voted after a specified period
- Producing a beautiful HTML report with copy-to-clipboard functionality

## 📋 Features

- ✅ Fetches active proposals from Snapshot GraphQL API
- ✅ Tracks voting status for specific council members
- ✅ Configurable alert threshold (default: 5 days)
- ✅ Generates a modern, responsive HTML report
- ✅ One-click copy of Ethereum addresses
- ✅ Direct links to proposals on Snapshot
- ✅ Suitable for scheduled execution (cron job)

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Internet connection (to access Snapshot API)

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure the environment:**

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` if you want to change any defaults:
```env
# Snapshot space to monitor
SNAPSHOT_SPACE=council.graphprotocol.eth

# Number of days before alerting for non-voters
ALERT_THRESHOLD_DAYS=5

# Path to file containing council member wallet addresses
WALLETS_FILE=wallets.txt

# Output HTML file path
OUTPUT_HTML=index.html
```

4. **Add council member wallet addresses:**

Edit `wallets.txt` and add the Ethereum wallet addresses of council members (one per line):
```
0x1234567890123456789012345678901234567890
0x2345678901234567890123456789012345678901
0x3456789012345678901234567890123456789012
```

**Note:** Lines starting with `#` are treated as comments and will be ignored.

### Usage

Run the monitoring script:
```bash
python monitor_council_votes.py
```

This will:
1. Fetch active proposals from Snapshot
2. Check voting status for all council members
3. Generate alerts for members who haven't voted after the threshold
4. Create an `index.html` file with the full report

Open `index.html` in your browser to view the report.

## 📅 Scheduling (Recommended)

To run the monitor automatically every 24 hours on a VPS:

### Using Cron (Linux/Unix/macOS)

1. Make the script executable:
```bash
chmod +x monitor_council_votes.py
```

2. Edit your crontab:
```bash
crontab -e
```

3. Add a line to run daily at 9 AM:
```bash
0 9 * * * cd /path/to/grump && /usr/bin/python3 monitor_council_votes.py >> /path/to/logs/monitor.log 2>&1
```

**Note:** Replace `/path/to/grump` with the actual path to this directory.

### Using systemd timer (Linux)

1. Create a service file `/etc/systemd/system/graph-council-monitor.service`:
```ini
[Unit]
Description=The Graph Council Voting Monitor
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/path/to/grump
ExecStart=/usr/bin/python3 monitor_council_votes.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

2. Create a timer file `/etc/systemd/system/graph-council-monitor.timer`:
```ini
[Unit]
Description=Run Graph Council Monitor daily
Requires=graph-council-monitor.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

3. Enable and start the timer:
```bash
sudo systemctl enable graph-council-monitor.timer
sudo systemctl start graph-council-monitor.timer
```

## 📊 HTML Report Features

The generated `index.html` report includes:

- **Summary Dashboard:** Overview of active proposals, council members, and alerts
- **Alert Section:** Highlighted warnings for members who haven't voted
- **Proposal Details:** Complete list of active proposals with voting statistics
- **Copy Functionality:** One-click copy buttons for all Ethereum addresses
- **Direct Links:** Quick access to view proposals on Snapshot
- **Responsive Design:** Works on desktop, tablet, and mobile devices

## 🔧 Configuration Options

### Environment Variables (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SNAPSHOT_SPACE` | `council.graphprotocol.eth` | The Snapshot space to monitor |
| `ALERT_THRESHOLD_DAYS` | `5` | Number of days before alerting for non-voters |
| `WALLETS_FILE` | `wallets.txt` | Path to file containing council member addresses |
| `OUTPUT_HTML` | `index.html` | Output HTML file path |

### Wallet File Format

The wallet file supports:
- One Ethereum address per line
- Comments (lines starting with `#`)
- Empty lines (ignored)
- Addresses in any case (automatically normalized to lowercase)

Example:
```
# The Graph Council Members
0xAddress1...
0xAddress2...

# Backup addresses
# 0xAddress3...
```

## 🛠️ Troubleshooting

### Common Issues

**"Wallets file not found"**
- Ensure `wallets.txt` exists in the project directory
- Check the `WALLETS_FILE` path in your `.env` file

**"API request failed"**
- Check your internet connection
- Snapshot API might be temporarily unavailable (retry later)
- Check for API rate limiting

**No proposals showing**
- Verify that there are active proposals on the Snapshot space
- Check that `SNAPSHOT_SPACE` is configured correctly

**HTML not displaying correctly**
- Ensure the entire HTML file was generated (check file size)
- Try opening in a different browser
- Check browser console for JavaScript errors

## 📝 Example Output

Console output:
```
============================================================
The Graph Council Voting Monitor
============================================================
Space: council.graphprotocol.eth
Alert threshold: 5 days
Output: index.html
============================================================

Loading council member wallets...
Loaded 6 council member addresses

Fetching active proposals from Snapshot...

Found 2 active proposal(s)
Generated 3 alert(s)

Generating HTML report: index.html
✓ Report generated successfully!
✓ Open index.html in your browser to view the report

⚠️  ALERTS:
  • 0x12345678... hasn't voted on 'GGP-001: Treasury Allocation' (7 days)
  • 0x23456789... hasn't voted on 'GGP-001: Treasury Allocation' (7 days)
  • 0x34567890... hasn't voted on 'GGP-002: Protocol Update' (6 days)
```

## 🔒 Security Notes

- Never commit your `.env` file with sensitive information to version control
- The `.gitignore` is configured to exclude `.env` automatically
- Council member addresses are public on the blockchain, so `wallets.txt` can be committed
- Consider restricting access to the generated HTML if it contains sensitive information

## 🤝 Contributing

Feel free to submit issues or pull requests to improve this tool!

## 📄 License

This tool is provided as-is for monitoring The Graph Council voting activity.

## 🔗 Useful Links

- [The Graph Council Snapshot Space](https://snapshot.org/#/council.graphprotocol.eth)
- [Snapshot Documentation](https://docs.snapshot.org/)
- [The Graph Protocol](https://thegraph.com/)

---

**Last Updated:** October 2025

