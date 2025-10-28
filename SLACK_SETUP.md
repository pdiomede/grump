# Slack Integration Setup Guide

## ✅ What Was Added

The Graph Council Voting Monitor now includes Slack integration! Every time the script runs, it will send notifications to Slack for any proposals that:
- Are older than the alert threshold (default: 5 days)
- Have council members who haven't voted yet

## 🚀 Quick Setup

### Step 1: Create Your `.env` File

Create a file named `.env` in the project root directory with the following content:

```env
# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR_WORKSPACE_ID/YOUR_CHANNEL_ID/YOUR_SECRET_TOKEN

# Snapshot Configuration
SNAPSHOT_SPACE=council.graphprotocol.eth

# Alert Settings
ALERT_THRESHOLD_DAYS=5

# File Paths
WALLETS_FILE=wallets.txt
OUTPUT_HTML=index.html

# Display Settings
COUNCIL_MEMBERS_COUNT=6
SHOW_COMPLETED_PROPOSALS=N
```

**Important:** Replace the `SLACK_WEBHOOK_URL` with your actual webhook URL.

### Step 2: Test the Integration

Run the script:

```bash
python monitor_council_votes.py
```

You should see output like:

```
============================================================
The Graph Council Voting Monitor
Version: 0.1.0
...
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
```

## 📨 Message Format

Each Slack notification will look like this:

```
🤖 Reminder: GGP-XXX: Treasury Allocation has 2 missing votes, and is ending in 3 days.
Missing votes in the last 5 days:
@0x1234567890123456789012345678901234567890
@0x2345678901234567890123456789012345678901

Please cast your vote here asap: https://snapshot.org/#/council.graphprotocol.eth/proposal/0xabc...
Thank you!
```

## 🔧 Configuration

### Disable Slack Notifications

To disable Slack notifications, simply remove the `SLACK_WEBHOOK_URL` from your `.env` file or set it to an empty string:

```env
SLACK_WEBHOOK_URL=
```

The script will skip Slack notifications and show:
```
⚠️  Slack webhook URL not configured - skipping Slack notification
```

### Adjust Alert Threshold

Change when alerts are sent by adjusting `ALERT_THRESHOLD_DAYS`:

```env
ALERT_THRESHOLD_DAYS=3  # Send alerts after 3 days instead of 5
```

## 📝 What Changed

### New Files
- `.env` (you need to create this)
- `SLACK_SETUP.md` (this file)

### Modified Files
- `monitor_council_votes.py` - Added Slack notification function
- `README.md` - Added Slack integration documentation

### New Function
- `send_slack_notification()` - Sends formatted messages to Slack for each proposal with missing votes

## 🆘 Troubleshooting

### "Slack webhook URL not configured"
- Make sure you created the `.env` file in the project root
- Verify `SLACK_WEBHOOK_URL` is set correctly
- The URL should start with `https://hooks.slack.com/services/`

### "Failed to send notification"
- Check your internet connection
- Verify the webhook URL is correct and active
- Check Slack webhook settings in your workspace

### No messages in Slack
- Make sure there are proposals with missing votes older than the threshold
- Check if the webhook is posting to the correct channel
- Verify the webhook hasn't been revoked in Slack settings

## 🔗 Resources

- [Slack Incoming Webhooks Documentation](https://api.slack.com/messaging/webhooks)
- [The Graph Council Snapshot Space](https://snapshot.org/#/council.graphprotocol.eth)

---

**Version:** 0.0.4  
**Last Updated:** October 28, 2025

