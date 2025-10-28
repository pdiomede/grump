#!/usr/bin/env python3
"""
The Graph Council Voting Monitor
Monitors Snapshot proposals and tracks council member voting activity
"""

# Version
VERSION = "0.2.0"
LAST_UPDATE = "2025-10-28"

import os
import sys
import json
import re
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Set
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SNAPSHOT_API_URL = "https://hub.snapshot.org/graphql"
SNAPSHOT_SPACE = os.getenv("SNAPSHOT_SPACE", "council.graphprotocol.eth")
ALERT_THRESHOLD_DAYS = int(os.getenv("ALERT_THRESHOLD_DAYS", "5"))
WALLETS_FILE = os.getenv("WALLETS_FILE", "wallets.txt")
OUTPUT_HTML = os.getenv("OUTPUT_HTML", "index.html")
COUNCIL_MEMBERS_COUNT = int(os.getenv("COUNCIL_MEMBERS_COUNT", "6"))
SHOW_COMPLETED_PROPOSALS = os.getenv("SHOW_COMPLETED_PROPOSALS", "N").upper() == "Y"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_MENTION_USERS = os.getenv("SLACK_MENTION_USERS", "")
POST_TO_SLACK = os.getenv("POST_TO_SLACK", "N").upper() == "Y"
PROPOSAL_MAX_AGE_DAYS = int(os.getenv("PROPOSAL_MAX_AGE_DAYS", "10"))
FUN_MODE = os.getenv("FUN_MODE", "N").upper() == "Y"


def load_council_wallets() -> List[str]:
    """Load council member wallet addresses from file"""
    wallets = []
    wallet_path = Path(WALLETS_FILE)
    
    if not wallet_path.exists():
        print(f"Error: Wallets file '{WALLETS_FILE}' not found!")
        sys.exit(1)
    
    with open(wallet_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                # Normalize to lowercase for comparison
                wallets.append(line.lower())
    
    return wallets


def query_snapshot(query: str, variables: dict = None) -> dict:
    """Execute a GraphQL query against Snapshot API"""
    try:
        response = requests.post(
            SNAPSHOT_API_URL,
            json={"query": query, "variables": variables or {}},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL errors: {data['errors']}")
            return None
            
        return data.get("data")
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None


def fetch_active_proposals() -> List[Dict]:
    """Fetch active proposals from the council space"""
    query = """
    query Proposals($space: String!) {
      proposals(
        first: 50,
        where: {
          space: $space,
          state: "active"
        },
        orderBy: "created",
        orderDirection: desc
      ) {
        id
        title
        body
        choices
        start
        end
        state
        author
        created
      }
    }
    """
    
    variables = {"space": SNAPSHOT_SPACE}
    result = query_snapshot(query, variables)
    
    if result and "proposals" in result:
        return result["proposals"]
    return []


def fetch_votes_for_proposal(proposal_id: str) -> List[Dict]:
    """Fetch all votes for a specific proposal"""
    query = """
    query Votes($proposal: String!) {
      votes(
        first: 1000,
        where: {
          proposal: $proposal
        }
      ) {
        id
        voter
        choice
        created
      }
    }
    """
    
    variables = {"proposal": proposal_id}
    result = query_snapshot(query, variables)
    
    if result and "votes" in result:
        return result["votes"]
    return []


def calculate_days_since(timestamp: int) -> int:
    """Calculate days since a Unix timestamp"""
    created_date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - created_date
    return delta.days


def analyze_voting_status(council_wallets: List[str]) -> Dict:
    """Analyze voting status for all active proposals"""
    proposals = fetch_active_proposals()
    
    if not proposals:
        return {
            "proposals": [],
            "alerts": [],
            "summary": {
                "total_proposals": 0,
                "total_alerts": 0
            }
        }
    
    # Filter proposals by max age
    now = datetime.now(timezone.utc)
    filtered_proposals = []
    for proposal in proposals:
        created_date = datetime.fromtimestamp(proposal["created"], tz=timezone.utc)
        days_old = (now - created_date).days
        if days_old <= PROPOSAL_MAX_AGE_DAYS:
            filtered_proposals.append(proposal)
    
    if not filtered_proposals:
        return {
            "proposals": [],
            "alerts": [],
            "summary": {
                "total_proposals": 0,
                "total_alerts": 0
            }
        }
    
    results = []
    all_alerts = []
    
    for proposal in filtered_proposals:
        proposal_id = proposal["id"]
        proposal_title = proposal["title"]
        created_timestamp = proposal["created"]
        end_timestamp = proposal["end"]
        days_old = calculate_days_since(created_timestamp)
        
        # Calculate days left until proposal ends
        now = datetime.now(timezone.utc)
        end_date = datetime.fromtimestamp(end_timestamp, tz=timezone.utc)
        days_left = (end_date - now).days
        
        # Fetch votes for this proposal
        votes = fetch_votes_for_proposal(proposal_id)
        voters = {vote["voter"].lower() for vote in votes}
        
        # Find who hasn't voted
        non_voters = []
        for wallet in council_wallets:
            if wallet not in voters:
                non_voters.append(wallet)
        
        # Generate alerts if threshold exceeded
        alerts_for_proposal = []
        if days_old >= ALERT_THRESHOLD_DAYS and non_voters:
            for wallet in non_voters:
                alert = {
                    "wallet": wallet,
                    "proposal_id": proposal_id,
                    "proposal_title": proposal_title,
                    "days_old": days_old
                }
                alerts_for_proposal.append(alert)
                all_alerts.append(alert)
        
        results.append({
            "id": proposal_id,
            "title": proposal_title,
            "created": created_timestamp,
            "end": end_timestamp,
            "days_old": days_old,
            "days_left": days_left,
            "total_votes": len(votes),
            "council_votes": len([w for w in council_wallets if w in voters]),
            "council_non_voters": non_voters,
            "alerts": alerts_for_proposal
        })
    
    return {
        "proposals": results,
        "alerts": all_alerts,
        "summary": {
            "total_proposals": len(filtered_proposals),
            "total_alerts": len(all_alerts)
        }
    }


def generate_html_report(data: Dict, council_wallets: List[str]) -> str:
    """Generate HTML report with voting status"""
    timestamp = datetime.now(timezone.utc).strftime("%d %b %Y at %H:%M (UTC)")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Graph Council Voting Monitor</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Poppins', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0C0A1D;
            min-height: 100vh;
            padding: 20px;
            color: #F8F6FF;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #0C0A1D;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            overflow: hidden;
            border: 1px solid #9CA3AF;
        }}
        
        .header {{
            background: #0C0A1D;
            color: #F8F6FF;
            padding: 30px;
            border-bottom: 1px solid #9CA3AF;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.2em;
            margin-bottom: 0.5rem;
            font-weight: 300;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 0.95rem;
            font-weight: 300;
        }}
        
        .header-link {{
            color: #F8F6FF;
            text-decoration: none;
            transition: opacity 0.3s ease;
        }}
        
        .header-link:hover {{
            opacity: 0.7;
            text-decoration: underline;
        }}
        
        .content {{
            padding: 30px;
            background: #0C0A1D;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
            padding: 25px 0;
            border-bottom: 1px solid #9CA3AF;
        }}
        
        .summary-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }}
        
        .summary-card h3 {{
            color: #9CA3AF;
            font-size: 14px;
            font-weight: 500;
            text-align: center;
        }}
        
        .summary-card .value {{
            color: #F8F6FF;
            font-size: 32px;
            font-weight: 600;
            text-align: center;
        }}
        
        .summary-card.alert-count .value {{
            color: #ef4444;
        }}
        
        .summary-card.proposal-count .value {{
            color: #fbbf24;
        }}
        
        .summary-card.member-count .value {{
            color: #22c55e;
        }}
        
        .alert-section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #F8F6FF;
            font-weight: 500;
        }}
        
        .alert-box {{
            background: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #ef4444;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #ef4444;
        }}
        
        .alert-box.warning {{
            background: rgba(239, 68, 68, 0.15);
            border-left-color: #ef4444;
        }}
        
        .alert-title {{
            font-weight: 600;
            margin-bottom: 10px;
            color: #ef4444;
            font-size: 1.1rem;
        }}
        
        .alert-details {{
            color: #9CA3AF;
            margin-top: 8px;
            font-size: 14px;
        }}
        
        .wallet-address {{
            font-family: 'Courier New', monospace;
            background: rgba(156, 163, 175, 0.1);
            padding: 8px 12px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-top: 8px;
            font-size: 13px;
            border: 1px solid #9CA3AF;
            color: #F8F6FF;
        }}
        
        .copy-btn {{
            background: rgba(156, 163, 175, 0.2);
            color: #9CA3AF;
            border: 1px solid #9CA3AF;
            padding: 4px 12px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .copy-btn:hover {{
            background: rgba(156, 163, 175, 0.3);
            opacity: 0.8;
            transform: translateY(-1px);
        }}
        
        .copy-btn:active {{
            transform: scale(0.95);
        }}
        
        .copy-btn.copied {{
            background: #22c55e;
            color: #0C0A1D;
            border-color: #22c55e;
        }}
        
        .proposal-card {{
            background: rgba(156, 163, 175, 0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #9CA3AF;
            transition: all 0.2s ease;
        }}
        
        .proposal-card:hover {{
            background: #1a1825;
            transform: translateY(-2px);
        }}
        
        .proposal-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }}
        
        .proposal-title {{
            font-size: 1.2rem;
            font-weight: 500;
            color: #F8F6FF;
            flex: 1;
        }}
        
        .proposal-badge {{
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            border: 1px solid #22c55e;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            margin-left: 15px;
        }}
        
        .proposal-badge.old {{
            background: rgba(251, 191, 36, 0.2);
            color: #fbbf24;
            border-color: #fbbf24;
        }}
        
        .days-left-badge {{
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            border: 1px solid #22c55e;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            margin-left: 10px;
        }}
        
        .days-left-badge.urgent {{
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border-color: #ef4444;
        }}
        
        .days-left-badge.soon {{
            background: rgba(251, 191, 36, 0.2);
            color: #fbbf24;
            border-color: #fbbf24;
        }}
        
        .proposal-alerts {{
            margin-top: 15px;
        }}
        
        .proposal-alerts .alert-box {{
            margin-bottom: 0;
        }}
        
        .proposal-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .stat {{
            font-size: 14px;
            color: #9CA3AF;
        }}
        
        .stat strong {{
            color: #F8F6FF;
        }}
        
        .stat .vote-count {{
            font-weight: 600;
        }}
        
        .stat .vote-count.all-voted {{
            color: #22c55e;
        }}
        
        .stat .vote-count.most-voted {{
            color: #fbbf24;
        }}
        
        .stat .vote-count.few-voted {{
            color: #ef4444;
        }}
        
        .non-voters {{
            background: rgba(156, 163, 175, 0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border: 1px solid #9CA3AF;
        }}
        
        .non-voters-title {{
            font-weight: 600;
            margin-bottom: 12px;
            color: #ef4444;
            font-size: 14px;
        }}
        
        .no-alerts {{
            text-align: center;
            padding: 50px;
            color: #22c55e;
            font-size: 1.2rem;
        }}
        
        .no-alerts::before {{
            content: "✓";
            display: block;
            font-size: 4rem;
            margin-bottom: 20px;
        }}
        
        .footer {{
            padding: 20px 30px;
            background: #0C0A1D;
            color: #9CA3AF;
            font-size: 14px;
            margin-top: 0;
            border-top: 1px solid #9CA3AF;
        }}
        
        .footer-content {{
            max-width: 1140px;
            margin: 0 auto;
        }}
        
        .footer-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .footer-left {{
            text-align: left;
            flex: 0 0 auto;
        }}
        
        .footer-right {{
            text-align: right;
            flex: 0 0 auto;
        }}
        
        .footer a {{
            color: #9CA3AF;
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        
        .footer a:hover {{
            color: #F8F6FF;
            text-decoration: underline;
        }}
        
        .version {{
            font-weight: 600;
            color: #9CA3AF;
        }}
        
        .footer-separator {{
            color: #9CA3AF;
        }}
        
        .github-icon {{
            display: inline-block;
            width: 16px;
            height: 16px;
            vertical-align: middle;
            margin-right: 5px;
        }}
        
        .snapshot-link {{
            color: #9CA3AF;
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        
        .snapshot-link:hover {{
            color: #F8F6FF;
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            .footer-top {{
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }}
            
            .footer-left,
            .footer-right {{
                text-align: left;
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗳️ The Graph Council Voting Monitor</h1>
            <p><a href="https://snapshot.org/#/s:{SNAPSHOT_SPACE}" target="_blank" class="header-link">Tracking voting activity for The Graph Council</a></p>
            <p>Last updated: {timestamp}</p>
        </div>
        
        <div class="content">
"""
    
    # Filter proposals based on SHOW_COMPLETED_PROPOSALS setting
    proposals_to_display = data['proposals']
    if not SHOW_COMPLETED_PROPOSALS:
        # Hide proposals where all council members have voted
        proposals_to_display = [
            p for p in data['proposals'] 
            if p['council_votes'] < COUNCIL_MEMBERS_COUNT
        ]
    
    html += f"""
            <div class="summary">
                <div class="summary-card alert-count">
                    <h3>Active Alerts</h3>
                    <div class="value">{data['summary']['total_alerts']}</div>
                </div>
                <div class="summary-card proposal-count">
                    <h3>Active Proposals</h3>
                    <div class="value">{len(proposals_to_display)}</div>
                </div>
                <div class="summary-card member-count">
                    <h3>Council Members</h3>
                    <div class="value">{COUNCIL_MEMBERS_COUNT}</div>
                </div>
            </div>
"""
    
    # Proposals section (with alerts inline)
    if proposals_to_display:
        
        html += """
            <div class="proposals-section">
                <h2 class="section-title">Active Alerts</h2>
"""
        
        for proposal in proposals_to_display:
            badge_class = "old" if proposal['days_old'] >= ALERT_THRESHOLD_DAYS else ""
            has_alerts = len(proposal.get('alerts', [])) > 0
            
            # Calculate voting percentage and determine color class
            council_votes = proposal['council_votes']
            vote_percentage = (council_votes / COUNCIL_MEMBERS_COUNT * 100) if COUNCIL_MEMBERS_COUNT > 0 else 0
            
            if council_votes == COUNCIL_MEMBERS_COUNT:
                vote_class = "all-voted"  # Green - all votes in
            elif vote_percentage >= 50:
                vote_class = "most-voted"  # Yellow - 50% or more but not all
            else:
                vote_class = "few-voted"  # Red - less than 50%
            
            # Determine days left badge color
            days_left = proposal.get('days_left', 0)
            
            # Green ONLY when all council members have voted
            if council_votes == COUNCIL_MEMBERS_COUNT:
                days_left_class = ""  # Green - all voted (success)
            # Red when less than 2 days and not all voted (urgent)
            elif days_left < 2:
                days_left_class = "urgent"  # Red - urgent, not all voted
            # Yellow for all other cases when not all voted
            else:
                days_left_class = "soon"  # Yellow - not all voted yet
            
            days_left_text = f"{days_left} day{'s' if days_left != 1 else ''} left" if days_left >= 0 else "Ended"
            
            html += f"""
                <div class="proposal-card">
                    <div class="proposal-header">
                        <div class="proposal-title">{proposal['title']}</div>
                        <div>
                            <span class="proposal-badge {badge_class}">{proposal['days_old']} days old</span>
                            <span class="days-left-badge {days_left_class}">{days_left_text}</span>
                        </div>
                    </div>
                    <div class="proposal-stats">
                        <div class="stat">
                            <strong>Total Votes:</strong> {proposal['total_votes']}
                        </div>
                        <div class="stat">
                            <strong>Council Votes:</strong> <span class="vote-count {vote_class}">{council_votes}/{COUNCIL_MEMBERS_COUNT}</span>
                        </div>
                    </div>
"""
            
            # Show alerts for this proposal if any
            if has_alerts and proposal['days_old'] >= ALERT_THRESHOLD_DAYS:
                html += f"""
                    <div class="proposal-alerts">
                        <div class="alert-box warning">
                            <div class="alert-title">
                                ⚠️ {len(proposal['alerts'])} Council Member(s) Haven't Voted (Proposal is {proposal['days_old']} days old)
                            </div>
"""
                
                for wallet in proposal['council_non_voters']:
                    html += f"""
                            <div class="alert-details">
                                <div class="wallet-address">
                                    <span class="wallet-text">{wallet}</span>
                                    <button class="copy-btn" onclick="copyToClipboard('{wallet}', this)">
                                        Copy
                                    </button>
                                </div>
                            </div>
"""
                
                html += """
                        </div>
                    </div>
"""
            elif proposal['council_non_voters']:
                # Show non-voters but without alert styling (under threshold)
                html += f"""
                    <div class="non-voters">
                        <div class="non-voters-title">
                            Council Members Who Haven't Voted Yet ({len(proposal['council_non_voters'])}):
                        </div>
"""
                
                for wallet in proposal['council_non_voters']:
                    html += f"""
                        <div class="wallet-address">
                            <span class="wallet-text">{wallet}</span>
                            <button class="copy-btn" onclick="copyToClipboard('{wallet}', this)">
                                Copy
                            </button>
                        </div>
"""
                
                html += """
                    </div>
"""
            
            html += f"""
                    <div style="margin-top: 1rem;">
                        <a href="https://snapshot.org/#/{SNAPSHOT_SPACE}/proposal/{proposal['id']}" 
                           class="snapshot-link" target="_blank">
                            View on Snapshot →
                        </a>
                    </div>
                </div>
"""
        
        html += """
            </div>
"""
    else:
        if FUN_MODE:
            html += """
            <div class="no-alerts">
                🎉 Woohoo! Nothing to see here. Everyone's chilling! 😎
            </div>
"""
        else:
            html += """
            <div class="no-alerts">
                All clear! No recent proposals requiring attention.
            </div>
"""
    
    # Show success message if no alerts at all
    if data['summary']['total_alerts'] == 0 and len(proposals_to_display) > 0:
        if FUN_MODE:
            html += """
            <div class="no-alerts" style="padding: 50px;">
                <img src="./pedro.jpg" alt="Pedro approves!" style="max-width: 300px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 20px;">
                <div style="font-size: 1.5rem; margin-top: 20px;">🎊 Amazing! The council is on fire! Everyone voted! 🔥</div>
            </div>
"""
        else:
            html += """
            <div class="no-alerts">
                ✅ Excellent! All council members are up to date with their votes.
            </div>
"""
    
    html += f"""
        </div>
        
        <div class="footer">
            <div class="footer-content">
                <div class="footer-top">
                    <div class="footer-left">
                        <a href="https://snapshot.org/#/s:{SNAPSHOT_SPACE}" target="_blank">Monitoring Snapshot votes for The Graph Council</a>
                    </div>
                    <div class="footer-right">
                        <span class="version">v{VERSION}</span>
                        <span class="footer-separator">-</span>
                        <svg class="github-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg><a href="https://github.com/pdiomede/grump" target="_blank">View repo on GitHub</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function copyToClipboard(text, button) {{
            navigator.clipboard.writeText(text).then(function() {{
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                button.classList.add('copied');
                
                setTimeout(function() {{
                    button.textContent = originalText;
                    button.classList.remove('copied');
                }}, 2000);
            }}, function(err) {{
                console.error('Failed to copy: ', err);
                alert('Failed to copy to clipboard');
            }});
        }}
    </script>
</body>
</html>
"""
    
    return html


def format_proposal_title(title: str) -> str:
    """Format proposal title for Slack messages
    
    Converts: "GGP-0055 Deploying GRT token..."
    To: GGP-0055 - "Deploying GRT token..."
    """
    # Match pattern like "GGP-0055" or "GIP-123" at the start
    match = re.match(r'^(G[A-Z]P-\d+)\s+(.+)$', title, re.IGNORECASE)
    if match:
        identifier = match.group(1)
        proposal_name = match.group(2)
        return f'{identifier} - "{proposal_name}"'
    else:
        # If no pattern found, just add quotes around the whole title
        return f'"{title}"'


def send_slack_notification(data: Dict, council_wallets: List[str]) -> bool:
    """Send Slack notifications for proposals with alerts"""
    # Filter proposals that have alerts (days_old >= threshold and has non-voters)
    proposals_with_alerts = [
        p for p in data['proposals'] 
        if p['days_old'] >= ALERT_THRESHOLD_DAYS and p['council_non_voters']
    ]
    
    if not proposals_with_alerts:
        if POST_TO_SLACK:
            print("\n✓ No alerts to send to Slack")
        else:
            print("\n✓ No alerts to save to file")
        return True
    
    # Check if we should post to Slack or save to file
    if POST_TO_SLACK:
        if not SLACK_WEBHOOK_URL:
            print("\n⚠️  Slack webhook URL not configured - skipping Slack notification")
            return False
        print(f"\n📤 Sending Slack notifications for {len(proposals_with_alerts)} proposal(s)...")
    else:
        print(f"\n💾 Saving Slack notifications to slack_message.txt for {len(proposals_with_alerts)} proposal(s)...")
    
    success_count = 0
    for proposal in proposals_with_alerts:
        try:
            # Extract proposal identifier (try to find GGP-XXX pattern or use title)
            title = proposal['title']
            formatted_title = format_proposal_title(title)
            proposal_id = proposal['id']
            
            # Calculate missing votes
            missing_votes = COUNCIL_MEMBERS_COUNT - proposal['council_votes']
            
            # Calculate days left (could be negative if ended)
            days_left = proposal['days_left']
            days_left_text = f"{days_left} day{'s' if days_left != 1 else ''}" if days_left >= 0 else "0 days (ENDED)"
            
            # Build the message
            if FUN_MODE:
                message_text = f"🚨 Hey team! {formatted_title} needs some love! {missing_votes} vote{'s' if missing_votes != 1 else ''} missing and it's ending in {days_left_text}! ⏰\n"
                message_text += f"Who forgot to vote in the last {ALERT_THRESHOLD_DAYS} days? 👀\n"
            else:
                message_text = f"🤖 Reminder: {formatted_title} has {missing_votes} missing vote{'s' if missing_votes != 1 else ''}, and is ending in {days_left_text}.\n"
                message_text += f"Missing votes in the last {ALERT_THRESHOLD_DAYS} days:\n"
            
            # Add non-voters (wallet addresses without @ symbol)
            for wallet in proposal['council_non_voters']:
                message_text += f"{wallet}\n"
            
            # Add link to proposal
            proposal_link = f"https://snapshot.org/#/{SNAPSHOT_SPACE}/proposal/{proposal_id}"
            if FUN_MODE:
                message_text += f"\n🎯 Cast your vote NOW and be a hero: {proposal_link}\n"
                message_text += "Let's gooooo! 🚀"
            else:
                message_text += f"\nPlease cast your vote here asap: {proposal_link}\n"
                message_text += "Thank you!"
            
            # Add dashboard link
            message_text += "\n\nFull Details here:\nhttps://dashboards.thegraph.foundation/grump/"
            
            # Add user mentions if configured
            if SLACK_MENTION_USERS:
                user_ids = [uid.strip() for uid in SLACK_MENTION_USERS.split(',') if uid.strip()]
                if user_ids:
                    mentions = ' '.join([f"<@{uid}>" for uid in user_ids])
                    message_text += f"\n\ncc {mentions}"
            
            # Send to Slack or save to file
            if POST_TO_SLACK:
                # Send to Slack
                payload = {
                    "text": message_text,
                    "unfurl_links": False,
                    "unfurl_media": False
                }
                
                response = requests.post(
                    SLACK_WEBHOOK_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"  ✓ Sent notification for: {title}")
                    success_count += 1
                else:
                    print(f"  ✗ Failed to send notification for: {title} (Status: {response.status_code})")
            else:
                # Save to file
                try:
                    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    with open("slack_message.txt", "a", encoding="utf-8") as f:
                        f.write(f"\n{'='*80}\n")
                        f.write(f"Timestamp: {timestamp}\n")
                        f.write(f"{'='*80}\n")
                        f.write(message_text)
                        f.write(f"\n{'='*80}\n\n")
                    print(f"  ✓ Saved notification for: {title}")
                    success_count += 1
                except IOError as e:
                    print(f"  ✗ Failed to save notification for: {title} (Error: {e})")
                
        except requests.exceptions.RequestException as e:
            if POST_TO_SLACK:
                print(f"  ✗ Error sending Slack notification for {proposal.get('title', 'Unknown')}: {e}")
        except Exception as e:
            print(f"  ✗ Unexpected error for {proposal.get('title', 'Unknown')}: {e}")
    
    if POST_TO_SLACK:
        print(f"\n📊 Slack notifications: {success_count}/{len(proposals_with_alerts)} sent successfully")
    else:
        print(f"\n📊 File notifications: {success_count}/{len(proposals_with_alerts)} saved successfully")
    
    return success_count == len(proposals_with_alerts)


def main():
    """Main execution function"""
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    print("=" * 60)
    print("The Graph Council Voting Monitor")
    print(f"Version: {VERSION}")
    print(f"Last Update: {LAST_UPDATE}")
    print(f"Current Run: {current_time}")
    print("=" * 60)
    print(f"Space: {SNAPSHOT_SPACE}")
    print(f"Proposal max age: {PROPOSAL_MAX_AGE_DAYS} days")
    print(f"Alert threshold: {ALERT_THRESHOLD_DAYS} days")
    print(f"Show completed proposals: {'Yes' if SHOW_COMPLETED_PROPOSALS else 'No'}")
    print(f"Output: {OUTPUT_HTML}")
    print("=" * 60)
    
    # Load council member wallets
    print("\nLoading council member wallets...")
    council_wallets = load_council_wallets()
    print(f"Loaded {len(council_wallets)} council member addresses")
    
    # Fetch and analyze data
    print("\nFetching active proposals from Snapshot...")
    data = analyze_voting_status(council_wallets)
    
    print(f"\nFound {data['summary']['total_proposals']} active proposal(s)")
    print(f"Generated {data['summary']['total_alerts']} alert(s)")
    
    # Generate HTML report
    print(f"\nGenerating HTML report: {OUTPUT_HTML}")
    html_content = generate_html_report(data, council_wallets)
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Report generated successfully!")
    print(f"✓ Open {OUTPUT_HTML} in your browser to view the report")
    
    # Send Slack notifications
    send_slack_notification(data, council_wallets)
    
    # Print summary to console
    if data['alerts']:
        print("\n⚠️  ALERTS:")
        for alert in data['alerts']:
            print(f"  • {alert['wallet'][:10]}... hasn't voted on '{alert['proposal_title']}' ({alert['days_old']} days)")
    else:
        print("\n✓ No alerts - all council members are up to date!")


if __name__ == "__main__":
    main()

