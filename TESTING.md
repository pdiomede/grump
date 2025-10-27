# Local Testing Guide

This guide explains how to test The Graph Council Voting Monitor on your local machine before deploying to production.

## Prerequisites

- Python 3.7 or higher
- Internet connection (for Snapshot API access)
- Council member wallet addresses

## Quick Test (5 minutes)

### Step 1: Check Python Version

```bash
python3 --version
```

Should show Python 3.7 or higher.

### Step 2: Navigate to Project Directory

```bash
cd /Users/pdiomede/Documents/WORK/_coding/controldeck/grump
```

### Step 3: Install Dependencies

```bash
pip3 install -r requirements.txt
```

Expected output:
```
Successfully installed requests-2.31.0 python-dotenv-1.0.0
```

### Step 4: Update Council Member Addresses

Edit `wallets.txt` with real Ethereum addresses:

```bash
nano wallets.txt
```

Replace the example addresses with actual Graph Council member addresses. Example:
```
# The Graph Council Members
0xYourRealAddress1...
0xYourRealAddress2...
0xYourRealAddress3...
0xYourRealAddress4...
0xYourRealAddress5...
0xYourRealAddress6...
```

Save and exit (Ctrl+X, then Y, then Enter).

**Where to find council member addresses:**
- Check The Graph governance documentation
- Look at previous votes on https://snapshot.org/#/council.graphprotocol.eth
- Ask The Graph community/team

### Step 5: Verify Configuration

Check your `.env` file:

```bash
cat .env
```

Should show:
```env
SNAPSHOT_SPACE=council.graphprotocol.eth
ALERT_THRESHOLD_DAYS=5
WALLETS_FILE=wallets.txt
OUTPUT_HTML=index.html
```

These defaults should work fine for testing.

### Step 6: Run the Script

```bash
python3 monitor_council_votes.py
```

**Expected Console Output:**

```
============================================================
The Graph Council Voting Monitor
Version: v0.0.1
Last Update: 2025-10-27
Current Run: 2025-10-27 17:45:00 UTC
============================================================
Space: council.graphprotocol.eth
Alert threshold: 5 days
Output: index.html
============================================================

Loading council member wallets...
Loaded 6 council member addresses

Fetching active proposals from Snapshot...

Found 2 active proposal(s)
Generated 1 alert(s)

Generating HTML report: index.html
✓ Report generated successfully!
✓ Open index.html in your browser to view the report

⚠️  ALERTS:
  • 0x12345678... hasn't voted on 'GGP-001: Example Proposal' (7 days)
```

### Step 7: View the Report

Open the generated HTML file in your browser:

**Option A - Command Line:**
```bash
open index.html
```

**Option B - Manual:**
1. Find `index.html` in the project folder
2. Double-click to open in your default browser

## What to Expect

### Successful Test Indicators ✅

1. **Console shows no errors**
   - Script completes without crashes
   - Shows number of proposals found
   - Shows number of alerts generated

2. **`index.html` file is created**
   ```bash
   ls -lh index.html
   ```
   Should show a file with size > 0 bytes

3. **HTML report displays correctly**
   - Beautiful, styled page loads in browser
   - Summary cards show numbers
   - Proposals are listed (if any active)
   - Alerts are shown (if any members haven't voted)

4. **Copy buttons work**
   - Click "Copy" button next to any address
   - Button should change to "Copied!" briefly
   - Address should be in your clipboard

### No Active Proposals? That's OK! ✅

If the script shows:
```
Found 0 active proposal(s)
Generated 0 alert(s)
```

This is **perfectly normal** if:
- There are currently no active proposals on Snapshot
- The voting period for proposals has ended

The HTML will show:
```
All council members have voted on active proposals!
```

This means the script is working correctly!

## Test with Different Configurations

### Test 1: Change Alert Threshold

Edit `.env`:
```env
ALERT_THRESHOLD_DAYS=1
```

Run again - you should see more alerts (if proposals are older than 1 day).

### Test 2: Change Output Location

Edit `.env`:
```env
OUTPUT_HTML=test_output.html
```

Run again - should create `test_output.html` instead.

### Test 3: Add Test Wallet

Add a fake address to `wallets.txt` to see it in non-voters list:
```
0x0000000000000000000000000000000000000000
```

This address definitely won't have voted, so it will appear in alerts.

## Troubleshooting

### Error: "Wallets file not found"

**Problem:** Can't find `wallets.txt`

**Solution:**
```bash
# Check if file exists
ls -la wallets.txt

# If missing, create it
touch wallets.txt
echo "0xYourAddress..." >> wallets.txt
```

### Error: "No module named 'requests'"

**Problem:** Dependencies not installed

**Solution:**
```bash
pip3 install -r requirements.txt
```

If that fails, try:
```bash
python3 -m pip install requests python-dotenv
```

### Error: "API request failed"

**Problem:** Can't reach Snapshot API

**Solution:**
1. Check internet connection
2. Try accessing https://hub.snapshot.org/graphql in browser
3. Wait a few minutes and try again (might be temporary)

### No Proposals Showing

**Problem:** Script runs but shows 0 proposals

**Possible Causes:**
1. **No active proposals** (most common - this is normal!)
   - Check manually: https://snapshot.org/#/council.graphprotocol.eth
   - If none are "Active" on Snapshot, the script is working correctly

2. **Wrong space name**
   - Verify `SNAPSHOT_SPACE=council.graphprotocol.eth` in `.env`

3. **API connectivity**
   - Test API manually (see below)

### HTML Not Displaying Correctly

**Problem:** HTML file opens but looks broken

**Solution:**
1. **Check file size:**
   ```bash
   ls -lh index.html
   ```
   Should be ~15-30 KB. If it's very small (<1 KB), something went wrong.

2. **Check for errors in console:**
   - Right-click on page → Inspect → Console tab
   - Look for JavaScript errors

3. **Try a different browser:**
   - Chrome, Firefox, Safari should all work

## Manual API Testing

To verify Snapshot API is accessible:

```bash
curl -X POST https://hub.snapshot.org/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ proposals(first: 1, where: {space: \"council.graphprotocol.eth\"}) { id title } }"}'
```

Should return JSON with proposal data.

## Testing the Quick Start Script

Test the wrapper script:

```bash
./run_monitor.sh
```

This should:
1. Check for dependencies
2. Install if needed
3. Run the monitor
4. Offer to open the HTML (on macOS)

## Verifying Generated HTML

Check the HTML was generated correctly:

```bash
# Check file size
ls -lh index.html

# View first few lines
head -20 index.html

# Count lines (should be several hundred)
wc -l index.html
```

Expected:
- File size: 15-30 KB
- Starts with: `<!DOCTYPE html>`
- Total lines: 200-400+ lines

## Performance Testing

Time how long the script takes:

```bash
time python3 monitor_council_votes.py
```

Expected:
- With internet: 2-10 seconds
- Most time is API requests to Snapshot

## Checking Logs in Test

Add verbose output for testing:

```bash
python3 monitor_council_votes.py 2>&1 | tee test_run.log
```

This saves output to `test_run.log` for review.

## Test Checklist

Before deploying to VPS, verify:

- [ ] Script runs without errors
- [ ] HTML file is generated
- [ ] HTML displays correctly in browser
- [ ] Council member addresses are correct
- [ ] Copy buttons work
- [ ] Links to Snapshot work
- [ ] Version number shows correctly
- [ ] Timestamp is in UTC
- [ ] Alert threshold works as expected

## Next Steps

Once local testing is successful:

1. **Commit your changes** (if using git)
   ```bash
   git add .
   git commit -m "Configure for production"
   ```

2. **Deploy to VPS**
   - Follow `DEPLOY.md` guide

3. **Test on VPS**
   - Run manually once to verify
   - Check HTML is accessible via web

4. **Set up automation**
   - Configure cron job
   - Monitor logs for first few runs

## Getting Real Council Addresses

If you don't have the real council member addresses yet:

### Option 1: Check Previous Votes on Snapshot

1. Go to https://snapshot.org/#/council.graphprotocol.eth
2. Click on any proposal
3. Scroll to votes section
4. Look for addresses that frequently vote
5. Copy addresses of council members

### Option 2: Check The Graph Documentation

- Visit The Graph governance documentation
- Look for "Council Members" section
- Copy the official wallet addresses

### Option 3: Use Test Addresses Temporarily

For initial testing, you can use these test addresses:
```
0x0000000000000000000000000000000000000001
0x0000000000000000000000000000000000000002
0x0000000000000000000000000000000000000003
0x0000000000000000000000000000000000000004
0x0000000000000000000000000000000000000005
0x0000000000000000000000000000000000000006
```

These won't have voted, so you'll see them in alerts (which proves the alert system works).

## Example Test Session

Here's what a complete test session looks like:

```bash
# 1. Navigate to project
cd /Users/pdiomede/Documents/WORK/_coding/controldeck/grump

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Update wallets (edit with nano/vim/your editor)
nano wallets.txt

# 4. Run the monitor
python3 monitor_council_votes.py

# 5. Open the report
open index.html

# 6. Success! 🎉
```

## Common Test Scenarios

### Scenario 1: Active Proposal with All Votes ✅
- **Result:** Green success message
- **Expected:** "All council members have voted"

### Scenario 2: Active Proposal with Missing Votes ⚠️
- **Result:** Alert section with warnings
- **Expected:** List of non-voters with copy buttons

### Scenario 3: No Active Proposals ✅
- **Result:** Empty proposals list
- **Expected:** "0 active proposals" in summary

### Scenario 4: Multiple Active Proposals 📊
- **Result:** Multiple proposal cards
- **Expected:** Each shows voting status separately

## Support

If you encounter issues during local testing:

1. Check this troubleshooting section
2. Review console error messages
3. Verify all prerequisites are met
4. Check `wallets.txt` format
5. Test internet connectivity
6. Try with test wallet addresses first

---

**Ready for Production?** Once local testing succeeds, follow `DEPLOY.md` to deploy to your VPS! 🚀

