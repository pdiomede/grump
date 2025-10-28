# The Graph Council Voting Monitor

A Python-based monitoring tool that tracks voting activity on The Graph Council's governance proposals via Snapshot and alerts when council members haven't voted after a configurable threshold (default: 5 days).

## 🎯 Purpose

The Graph Council consists of 6 members who vote on Graph Governance Proposals (GGPs) posted on https://snapshot.org/#/council.graphprotocol.eth. This tool helps ensure full participation by:

- Monitoring active proposals on Snapshot
- Tracking which council members have/haven't voted
- Generating alerts when members haven't voted after a specified period
- Producing a beautiful HTML report with copy-to-clipboard functionality

## 🔧 How It Works

### Script Logic Flow

1. **Load Configuration**
   - Reads environment variables from `.env` file
   - Loads council member wallet addresses from `wallets.txt`
   - Sets alert threshold and output paths

2. **Fetch Active Proposals**
   - Connects to Snapshot GraphQL API (`https://hub.snapshot.org/graphql`)
   - Queries for active proposals in the `council.graphprotocol.eth` space
   - Retrieves proposal metadata: title, creation date, end date, state

3. **Fetch Voting Data**
   - For each active proposal, fetches all votes
   - Extracts voter addresses (normalized to lowercase)
   - Creates a set of voters for quick lookup

4. **Analyze Voting Status**
   - Compares council member addresses against voters
   - Identifies non-voters for each proposal
   - Calculates:
     - Days since proposal creation
     - Days remaining until voting ends
     - Voting percentage (council votes / total council members)

5. **Generate Alerts**
   - Creates alerts for proposals older than threshold (default: 5 days)
   - Only alerts for council members who haven't voted
   - Alerts are displayed inline within each proposal card

6. **Color-Code Metrics**
   - **Voting Status:**
     - 🟢 Green: All council members voted (100%)
     - 🟡 Yellow: ≥50% voted but not all
     - 🔴 Red: <50% voted
   - **Time Remaining:**
     - 🟢 Green: 5+ days left
     - 🟡 Yellow: 2-4 days left
     - 🔴 Red: <2 days left

7. **Generate HTML Report**
   - Creates a static HTML dashboard with:
     - Summary cards (alerts, proposals, members)
     - Proposal cards with voting statistics
     - Inline alerts for non-voters
     - Copy-to-clipboard buttons
     - Direct links to Snapshot
   - Uses dark theme with Poppins font
   - Fully responsive design

### Data Flow Diagram

```
┌─────────────────┐
│  Configuration  │
│  (.env, txt)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Snapshot API   │◄──── GraphQL Query (Active Proposals)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vote Analysis  │◄──── Compare voters vs council members
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Alert Logic    │◄──── Check thresholds & generate alerts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTML Generator │◄──── Create styled dashboard
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   index.html    │◄──── Static report with all data
└─────────────────┘
```

### Key Algorithms

**Voting Percentage Calculation:**
```python
vote_percentage = (council_votes / COUNCIL_MEMBERS_COUNT) * 100
if council_votes == COUNCIL_MEMBERS_COUNT:
    color = "green"  # All voted
elif vote_percentage >= 50:
    color = "yellow"  # Most voted
else:
    color = "red"  # Few voted
```

**Days Left Calculation:**
```python
now = datetime.now(timezone.utc)
end_date = datetime.fromtimestamp(end_timestamp, tz=timezone.utc)
days_left = (end_date - now).days
```

**Alert Threshold Check:**
```python
if days_old >= ALERT_THRESHOLD_DAYS and non_voters:
    generate_alert(proposal, non_voters)
```

## 📋 Features

- ✅ Fetches active proposals from Snapshot GraphQL API
- ✅ Tracks voting status for specific council members
- ✅ Configurable alert threshold (default: 5 days)
- ✅ Optional hiding of completed proposals (with all votes)
- ✅ Color-coded voting status and time remaining indicators
- ✅ Generates a modern, responsive HTML report
- ✅ One-click copy of Ethereum addresses
- ✅ Direct links to proposals on Snapshot
- ✅ **Slack integration** - sends notifications for proposals with missing votes
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
# Slack Configuration (optional - leave empty to disable)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Snapshot space to monitor
SNAPSHOT_SPACE=council.graphprotocol.eth

# Number of days before alerting for non-voters
ALERT_THRESHOLD_DAYS=5

# Path to file containing council member wallet addresses
WALLETS_FILE=wallets.txt

# Output HTML file path
OUTPUT_HTML=index.html

# Expected number of council members
COUNCIL_MEMBERS_COUNT=6

# Show proposals with all council members voted (Y/N)
SHOW_COMPLETED_PROPOSALS=N
```

4. **Add council member wallet addresses:**

Edit `wallets.txt` and add the Ethereum wallet addresses of council members (one per line):
```
0x1234567890123456789012345678901234567890
0x2345678901234567890123456789012345678901
0x3456789012345678901234567890123456789012
```

**Note:** Lines starting with `#` are treated as comments and will be ignored.

5. **Configure Slack notifications (Optional):**

To receive Slack notifications when proposals have missing votes:

a. Create a Slack incoming webhook:
   - Go to https://api.slack.com/messaging/webhooks
   - Click "Create your Slack app" 
   - Choose "From scratch" and select your workspace
   - Navigate to "Incoming Webhooks" and activate it
   - Click "Add New Webhook to Workspace"
   - Select the channel where you want notifications
   - Copy the Webhook URL

b. Add the webhook URL to your `.env` file:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR_WORKSPACE_ID/YOUR_CHANNEL_ID/YOUR_SECRET_TOKEN
```

**Slack Message Format:**

When a proposal has missing votes after the alert threshold, you'll receive a message like:

```
🤖 Reminder: GGP-XXX has 2 missing votes, and is ending in 3 days.
Missing votes in the last 5 days:
@0x1234567890123456789012345678901234567890
@0x2345678901234567890123456789012345678901

Please cast your vote here asap: https://snapshot.org/#/council.graphprotocol.eth/proposal/0xabc...
Thank you!
```

**Note:** If `SLACK_WEBHOOK_URL` is not set or empty, Slack notifications will be skipped.

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
| `SLACK_WEBHOOK_URL` | _(empty)_ | Slack webhook URL for notifications (optional) |
| `SNAPSHOT_SPACE` | `council.graphprotocol.eth` | The Snapshot space to monitor |
| `ALERT_THRESHOLD_DAYS` | `5` | Number of days before alerting for non-voters |
| `WALLETS_FILE` | `wallets.txt` | Path to file containing council member addresses |
| `OUTPUT_HTML` | `index.html` | Output HTML file path |
| `COUNCIL_MEMBERS_COUNT` | `6` | Expected number of council members |
| `SHOW_COMPLETED_PROPOSALS` | `N` | Show proposals with all votes (Y/N) |

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

📤 Sending Slack notifications for 2 proposal(s)...
  ✓ Sent notification for: GGP-001: Treasury Allocation
  ✓ Sent notification for: GGP-002: Protocol Update

📊 Slack notifications: 2/2 sent successfully

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

**Last Updated:** October 28, 2025 (v0.0.4)

