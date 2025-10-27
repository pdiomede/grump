# How to Get Real Graph Council Member Addresses

## Quick Method: Check Snapshot Directly

1. **Go to the Snapshot space:**
   https://snapshot.org/#/council.graphprotocol.eth

2. **Click on any recent proposal** (one that has votes)

3. **Scroll down to the "Votes" section**

4. **Look for addresses that vote frequently** - these are likely council members

5. **Copy the 6 most frequent voters** (these are the council members)

## Example:

When you see votes like:
```
✓ 0xAbc123... voted "For"
✓ 0xDef456... voted "For"
✓ 0x789Xyz... voted "Against"
```

These are the addresses you want to add to `wallets.txt`

## Finding Official List

### Option 1: The Graph Governance Forum
- Visit: https://forum.thegraph.com/
- Search for "council members" or "GGP" (Graph Governance Proposal)
- Look for official announcements listing council member addresses

### Option 2: The Graph Discord
- Join The Graph Discord
- Ask in #governance channel for official council member addresses

### Option 3: Check Previous GGPs
- Look at proposals that specifically elected or confirmed council members
- These proposals will list the official addresses

## Once You Have Real Addresses:

Edit `wallets.txt`:

```bash
nano /Users/pdiomede/Documents/WORK/_coding/controldeck/grump/wallets.txt
```

Replace with real addresses:
```
# The Graph Council Members (replace with actual addresses)
0xRealAddress1...
0xRealAddress2...
0xRealAddress3...
0xRealAddress4...
0xRealAddress5...
0xRealAddress6...
```

Save and run again:
```bash
python3 monitor_council_votes.py
```

Now you'll see **real voting data** for actual council members!

