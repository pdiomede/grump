# Changelog

All notable changes to The Graph Council Voting Monitor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.1] - 2025-10-28

### Changed

#### Dashboard Messages
- **Improved Success Messages**
  - "No active proposals found." → "All clear! No recent proposals requiring attention."
  - "✅ All council members have voted on active proposals!" → "✅ Excellent! All council members are up to date with their votes."
  - More positive and encouraging tone
  - Clearer communication of status

**Before:**
- "No active proposals found."
- "All council members have voted on active proposals!"

**After:**
- "All clear! No recent proposals requiring attention."
- "Excellent! All council members are up to date with their votes."

### Benefits
- More positive user experience
- Clearer status communication
- Professional and encouraging messaging
- Better reflects the purpose of filtering recent proposals

## [v0.1.0] - 2025-10-28

### Added

#### Dashboard Link in Slack Messages
- **Dashboard URL in Notifications**
  - Added link to dashboard at the end of each Slack notification
  - URL: https://dashboards.thegraph.foundation/grump/
  - Provides easy access to full voting details
  - Shows after "Thank you!" and before user mentions

### Changed

#### Slack Message Format
- **Enhanced Message with Dashboard Link**
  - Messages now include "Full Details here:" section
  - Direct link to the voting monitor dashboard
  - Allows team to quickly review all proposals and voting status
  - Positioned between main message and cc mentions

**Updated Message Format:**
```
🤖 Reminder: [Proposal details]
[Missing votes]

Please cast your vote here asap: [Snapshot link]
Thank you!

Full Details here:
https://dashboards.thegraph.foundation/grump/

cc @User1 @User2
```

### Benefits
- Quick access to comprehensive dashboard
- Single source of truth for all voting data
- Reduces need for multiple links
- Better user experience with centralized information

## [v0.0.9] - 2025-10-28

### Added

#### Proposal Age Filtering
- **PROPOSAL_MAX_AGE_DAYS Configuration Variable**
  - New `PROPOSAL_MAX_AGE_DAYS` environment variable (default: 10 days)
  - Only monitors proposals created within the last N days
  - Helps focus on recent proposals and ignore very old ones
  - Reduces noise from stale proposals

- **Age-Based Filtering Logic**
  - Proposals older than `PROPOSAL_MAX_AGE_DAYS` are automatically excluded
  - Filtering happens before vote analysis for efficiency
  - Count reflects only proposals within the age window
  - Console output shows the configured max age setting

### Changed

#### Proposal Analysis
- **analyze_voting_status() Function**
  - Now filters proposals by creation date before processing
  - Only includes proposals created within `PROPOSAL_MAX_AGE_DAYS`
  - Returns empty results if no proposals match age criteria
  - More efficient processing of recent proposals only

- **Console Output**
  - Added "Proposal max age: X days" to startup information
  - Helps verify the configuration is correct
  - Shows the age filter being applied

### Technical Details

**Configuration:**
```env
PROPOSAL_MAX_AGE_DAYS=10  # Only check proposals from last 10 days (default)
PROPOSAL_MAX_AGE_DAYS=30  # Check proposals from last 30 days
PROPOSAL_MAX_AGE_DAYS=365 # Check all active proposals (1 year window)
```

**Example:**
- Today is October 28, 2025
- `PROPOSAL_MAX_AGE_DAYS=10`
- Only proposals created on or after October 18, 2025 will be monitored
- Older proposals (e.g., from August) will be ignored

**Use Case:**
Before this change, a 69-day-old proposal (GGP-0055) was generating alerts even though it's very old. Now with `PROPOSAL_MAX_AGE_DAYS=10`, only recent proposals will be checked, reducing alert fatigue.

**Benefits:**
- Focus on recent proposals that need attention
- Reduce alert fatigue from very old proposals
- Faster execution (fewer proposals to process)
- Configurable - increase the window if needed
- Default of 10 days balances recency vs. coverage

**Implementation:**
- Filtering uses proposal creation timestamp
- Compares against current UTC time
- Simple integer day comparison (>= operator)
- Returns early if no proposals match criteria

## [v0.0.8] - 2025-10-28

### Added

#### Testing and Development Features
- **POST_TO_SLACK Configuration Variable**
  - New `POST_TO_SLACK` environment variable (Y/N)
  - Allows toggling between Slack and local file output
  - Default: N (save to file for testing)
  - Enables testing notifications before sending to Slack

- **Local File Output Mode**
  - When `POST_TO_SLACK=N`, messages are saved to `slack_message.txt`
  - Messages are **appended** (not overwritten)
  - Each message includes timestamp separator
  - Perfect for reviewing notifications before going live
  - Useful for debugging and testing message formatting

- **Timestamp Headers**
  - Each saved message includes UTC timestamp
  - Clear separators (80 equals signs) between messages
  - Easy to track when notifications were generated

#### .gitignore Updates
- Added `slack_message.txt` to `.gitignore`
- Prevents accidental commit of test messages
- Keeps repository clean

### Changed

#### Notification Logic
- **Dual Output Mode**
  - Function now supports both Slack posting and file saving
  - Automatic route selection based on `POST_TO_SLACK` setting
  - Different console messages for each mode
  - Independent error handling for file I/O vs. HTTP requests

- **Console Output**
  - When `POST_TO_SLACK=N`: "💾 Saving Slack notifications to slack_message.txt..."
  - When `POST_TO_SLACK=Y`: "📤 Sending Slack notifications..."
  - Summary adapts: "File notifications: X/Y saved successfully" vs. "Slack notifications: X/Y sent successfully"

### Technical Details

**Configuration:**
```env
POST_TO_SLACK=N  # Save to file for testing
POST_TO_SLACK=Y  # Send to Slack
```

**File Output Format:**
```
================================================================================
Timestamp: 2025-10-28 13:15:30 UTC
================================================================================
🤖 Reminder: GGP-0055 - "Proposal Title" has 2 missing votes...
[full message content]
================================================================================
```

**Benefits:**
- Test message formatting before sending to Slack
- Review notifications without spamming Slack channel
- Debug message content and formatting
- Archive of all generated notifications
- Safe development workflow

**Implementation:**
- File operations use UTF-8 encoding
- Append mode ensures no data loss
- IOError exception handling for file operations
- Separate error messages for file vs. Slack failures
- RequestException only caught when `POST_TO_SLACK=Y`

### Workflow

**Development/Testing:**
1. Set `POST_TO_SLACK=N`
2. Run script to generate messages
3. Review `slack_message.txt`
4. Adjust formatting as needed

**Production:**
1. Set `POST_TO_SLACK=Y`
2. Messages go directly to Slack
3. Team receives notifications

## [v0.0.7] - 2025-10-28

### Added

#### Proposal Title Formatting
- **format_proposal_title() Function**
  - New function to format proposal titles in Slack messages
  - Automatically detects GGP/GIP identifiers at the start of titles
  - Formats titles with quotes and proper separation
  - Supports various Graph proposal patterns (GGP, GIP, etc.)

### Changed

#### Slack Message Format
- **Enhanced Title Display**
  - Proposal titles now formatted with identifier and quoted name
  - Pattern: `GGP-XXXX - "Proposal Name"`
  - Improves readability and professional appearance
  - Works with all GxP-style identifiers (GGP, GIP, GAP, etc.)

**Before:**
```
🤖 Reminder: GGP-0055 Deploying GRT token to Avalanche, Base, and Solana has 2 missing votes...
```

**After:**
```
🤖 Reminder: GGP-0055 - "Deploying GRT token to Avalanche, Base, and Solana" has 2 missing votes...
```

### Technical Details

**Implementation:**
- Added `re` module import for regex pattern matching
- Regex pattern: `^(G[A-Z]P-\d+)\s+(.+)$` matches identifiers
- Falls back to quoting entire title if no pattern matches
- Case-insensitive matching for flexibility

**Supported Patterns:**
- GGP-0001, GGP-0055, etc. (Graph Governance Proposals)
- GIP-0001 (Graph Improvement Proposals)
- GAP-0001 (Graph Advancement Proposals)
- Any G[letter]P-[number] format

### Documentation
- Updated README.md with new message format example
- Shows properly formatted title with quotes and dash

## [v0.0.6] - 2025-10-28

### Changed

#### Slack Message Formatting
- **Wallet Address Display**
  - Removed "@" symbol prefix from wallet addresses in Slack notifications
  - Addresses now display as plain text (e.g., `0x1234...` instead of `@0x1234...`)
  - Cleaner message format and better readability
  - Avoids confusion with Slack user mentions which use `<@USER_ID>` format

**Before:**
```
Missing votes in the last 5 days:
@0x1234567890123456789012345678901234567890
```

**After:**
```
Missing votes in the last 5 days:
0x1234567890123456789012345678901234567890
```

### Documentation
- Updated README.md with corrected message format example
- Message format now shows wallet addresses without @ prefix

## [v0.0.5] - 2025-10-28

### Added

#### Slack User Mentions
- **SLACK_MENTION_USERS Configuration**
  - Added `SLACK_MENTION_USERS` environment variable for mentioning specific users
  - Supports comma-separated list of Slack User IDs (e.g., `U01234ABCDE,U56789FGHIJ`)
  - User IDs are permanent and work even when display names change
  - Optional feature - leave empty to disable mentions
  
- **CC Mentions in Notifications**
  - Slack notifications now include "cc @User1 @User2" at the end
  - Uses proper Slack mention format: `<@USER_ID>`
  - Mentioned users receive Slack notifications
  - Great for alerting team leads or coordinators
  
- **HOW_TO_GET_SLACK_USER_IDS.md**
  - Complete guide on finding Slack User IDs
  - Three methods: Copy member ID, profile URL, and API
  - Examples and testing instructions
  - Troubleshooting tips

#### Documentation Updates
- **README.md**
  - Added SLACK_MENTION_USERS to configuration instructions
  - Updated Slack message format example with cc mentions
  - Added configuration table entry for user mentions
  - Quick reference on how to get User IDs
  
### Changed
- **Slack Message Format**
  - Messages now optionally end with: `cc <@USER_ID1> <@USER_ID2>`
  - Appears in Slack as: `cc @Pedro @Andrew Clews`
  - Only included when SLACK_MENTION_USERS is configured

### Technical Details

**Configuration Example:**
```env
SLACK_MENTION_USERS=U01ABC123,U02DEF456
```

**Message Example:**
```
🤖 Reminder: GGP-XXX has 2 missing votes, and is ending in 3 days.
Missing votes in the last 5 days:
@0x1234...

Please cast your vote here asap: [link]
Thank you!

cc @Pedro @Andrew Clews
```

**Implementation:**
- Parses comma-separated User IDs from environment variable
- Formats mentions using Slack's `<@USER_ID>` syntax
- Appends to message only if User IDs are configured
- Supports multiple users with single or multiple spaces

### Benefits
- Direct notifications to team leads/coordinators
- Ensures key people are always alerted
- Works reliably even when users change display names
- Optional - no breaking changes for existing configurations

## [v0.0.4] - 2025-10-28

### Added

#### Slack Integration
- **Slack Webhook Notifications**
  - Added `SLACK_WEBHOOK_URL` configuration parameter to `.env` file
  - Automatic Slack notifications sent for proposals with missing votes
  - Notifications trigger when proposals exceed alert threshold (default: 5 days)
  - Each proposal with missing votes generates a separate notification message
  
- **Notification Message Format**
  - Shows proposal title (e.g., "GGP-XXX: Proposal Title")
  - Displays count of missing votes
  - Shows days remaining until proposal ends
  - Lists non-voting council member addresses with @ mentions
  - Includes direct link to vote on Snapshot
  - Professional reminder format with call-to-action
  
- **Smart Notification Logic**
  - Only sends notifications when there are actual alerts
  - Skips Slack integration gracefully if webhook URL not configured
  - Sends one message per proposal with missing votes
  - Detailed console output showing notification status
  - Error handling for network issues and failed sends
  - Success/failure tracking with summary report

#### Documentation
- **SLACK_SETUP.md**
  - Comprehensive setup guide for Slack webhook creation
  - Step-by-step configuration instructions
  - Message format examples
  - Troubleshooting section
  - Instructions for disabling notifications
  
- **Updated README.md**
  - Added Slack integration to features list
  - Webhook setup instructions with screenshots guide
  - Configuration table updated with `SLACK_WEBHOOK_URL`
  - Example console output with Slack notification logs
  - Security notes about webhook URLs

#### New Function
- `send_slack_notification(data, council_wallets)` function
  - Filters proposals with alerts (days_old >= threshold)
  - Iterates through each proposal needing attention
  - Formats custom message for each proposal
  - POSTs to Slack webhook with JSON payload
  - Returns success/failure status with detailed logging

### Changed
- **Main Execution Flow**
  - Added Slack notification call after HTML report generation
  - Console output now includes Slack notification status
  - Enhanced progress reporting with emoji indicators (📤, ✓, ✗, 📊)

- **Version Bump**
  - Updated VERSION to 0.0.4
  - Updated LAST_UPDATE to 2025-10-28
  - Reflects Slack integration addition

### Technical Details

**Configuration**
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Message Example**
```
🤖 Reminder: GGP-XXX has 2 missing votes, and is ending in 3 days.
Missing votes in the last 5 days:
@0x1234567890123456789012345678901234567890
@0x2345678901234567890123456789012345678901

Please cast your vote here asap: [link]
Thank you!
```

**Console Output**
```
📤 Sending Slack notifications for 2 proposal(s)...
  ✓ Sent notification for: GGP-001: Treasury Allocation
  ✓ Sent notification for: GGP-002: Protocol Update
📊 Slack notifications: 2/2 sent successfully
```

### Benefits
- Proactive team engagement via Slack channel
- Automated daily reminders for pending votes
- Reduced manual follow-up effort
- Improved voting participation
- Seamless integration with existing workflow
- Optional feature (can be disabled by not setting webhook)

## [v0.0.3] - 2025-10-27

### Added

#### Configuration
- **Hide Completed Proposals**
  - Added `SHOW_COMPLETED_PROPOSALS` parameter to `.env` file (default: N)
  - When set to "N", proposals with all council members voted (6/6) are hidden from the dashboard
  - When set to "Y", all proposals are displayed regardless of voting completion
  - Helps focus attention on proposals that still need votes
  - Active Proposals counter updates dynamically based on displayed proposals
  - Console output displays current setting for transparency

### Changed
- **Version Bump**
  - Updated VERSION to 0.0.3
  - Reflects new configuration feature addition

## [v0.0.2] - 2025-10-27

### Added

#### UI/UX Improvements
- **Days Left Counter**
  - Added "days left" badge for each proposal showing time remaining until voting ends
  - Smart color-coding based on voting completion:
    - 🟢 Green: ONLY when all council members have voted (6/6) - Success!
    - 🟡 Yellow: When votes are incomplete (default state)
    - 🔴 Red: Less than 2 days remaining AND votes still incomplete - Urgent!
  - Displays "Ended" status for closed proposals
  
- **Color-Coded Voting Statistics**
  - Council votes now display with color indicators:
    - 🟢 Green: All council members have voted (6/6)
    - 🟡 Yellow: 50%+ have voted but not all (3-5/6)
    - 🔴 Red: Less than 50% have voted (0-2/6)
  - Visual priority system for quick identification of voting status

- **Improved Header Design**
  - Changed emoji to 🗳️ (ballot box) for better voting representation
  - Made subtitle clickable with link to Snapshot space
  - Added smooth hover effects on header links

- **Enhanced Footer**
  - Redesigned footer with two-column layout matching sample.py
  - Left: Clickable link "Monitoring Snapshot votes for The Graph Council"
  - Right: Version info and GitHub repository link with icon
  - Responsive mobile layout (stacks vertically on small screens)

#### Configuration
- **Parametric Council Count**
  - Added `COUNCIL_MEMBERS_COUNT` parameter to `.env` file
  - Dynamic council member count throughout application
  - Default value: 6 members
  - Used for voting percentage calculations and display

#### Technical
- **Proposal End Time Tracking**
  - Now fetches and tracks proposal end timestamps
  - Calculates remaining time for active proposals
  - Enables time-based urgency indicators

### Changed
- **Alert Display Logic**
  - Removed separate alerts section
  - Alerts now displayed inline within proposal cards
  - Contextual alert presentation for better UX
  - Proposals show alerts only when threshold is exceeded

- **Summary Card Order**
  - Reordered summary cards by priority:
    1. Active Alerts (Red) - Most important
    2. Active Proposals (Yellow) - Needs monitoring
    3. Council Members (Green) - Status info

- **Version Format**
  - Changed VERSION format from "v0.0.1" to "0.0.1" (removed 'v' prefix)
  - Consistent version display across UI

### Improved
- **Dark Theme Consistency**
  - Applied sample.py color palette throughout
  - Background: `#0C0A1D` (dark navy)
  - Text: `#F8F6FF` (light lavender)
  - Borders: `#9CA3AF` (gray)
  - Font: Poppins for modern look

- **Interactive Elements**
  - All links have consistent hover effects
  - Smooth transitions (0.3s) for better UX
  - Clear visual feedback on interactive elements

- **Mobile Responsiveness**
  - Enhanced footer layout for mobile devices
  - Improved touch target sizes
  - Better text wrapping and spacing

### Fixed
- **Days Left Badge Logic**
  - Fixed badge to show green ONLY when all council members have voted
  - Yellow is now the default state for incomplete voting (regardless of time remaining)
  - Red only appears when less than 2 days remain AND voting is incomplete
  - Ensures clear visual indication of voting completion status

- **Footer Layout**
  - Fixed footer structure to match dashboard styling
  - Proper spacing and alignment
  - Consistent color scheme

## [v0.0.1] - 2025-10-27

### Initial Release 🎉

This is the first release of The Graph Council Voting Monitor - a tool to track voting activity on The Graph Council's governance proposals via Snapshot.

### Added

#### Core Features
- **Snapshot API Integration**
  - GraphQL queries to fetch active proposals from `council.graphprotocol.eth` space
  - Retrieval of all votes for each proposal
  - Automatic detection of council member voting status

- **Configurable Monitoring System**
  - Environment variable configuration via `.env` file
  - Customizable Snapshot space monitoring
  - Adjustable alert threshold (default: 5 days)
  - Flexible wallet list management via `wallets.txt`
  - Configurable output HTML file path

- **Voting Analysis**
  - Tracking of council member voting participation
  - Identification of non-voters on active proposals
  - Calculation of days elapsed since proposal creation
  - Alert generation when threshold is exceeded

- **HTML Report Generation**
  - Modern, responsive web interface
  - Beautiful gradient design with professional styling
  - Summary dashboard with key metrics
    - Active proposals count
    - Council members count
    - Active alerts count
  - Alert section highlighting non-voters with warning styling
  - Detailed proposal cards with:
    - Proposal title and age
    - Total votes and council member votes
    - List of council members who haven't voted
    - Direct links to Snapshot proposals
  - Copy-to-clipboard functionality for Ethereum addresses
  - Mobile-responsive design

#### Version Tracking
- `VERSION` constant set to "v0.0.1"
- `LAST_UPDATE` constant with release date
- Version display in console output
- Version and last update date in HTML report footer
- Timestamp of current run displayed in UTC format

#### Configuration Files
- `.env` - Environment configuration
- `.env.example` - Template for environment setup
- `wallets.txt` - Council member wallet addresses
- `requirements.txt` - Python dependencies (requests, python-dotenv)
- `.gitignore` - Git ignore rules for sensitive files

#### Scripts
- `monitor_council_votes.py` - Main monitoring script
- `run_monitor.sh` - Quick start wrapper script with dependency checks

#### Documentation
- `README.md` - Comprehensive user guide with:
  - Installation instructions
  - Configuration guide
  - Usage examples
  - Cron job setup for scheduling
  - Troubleshooting section
- `DEPLOY.md` - VPS deployment guide for Ubuntu with Nginx:
  - Step-by-step server setup
  - Nginx configuration
  - SSL/HTTPS setup with Let's Encrypt
  - Security hardening recommendations
  - Log rotation and maintenance
- `CHANGELOG.md` - This file, tracking all versions

#### Features Detail

**Alert System**
- Automatic detection of council members who haven't voted
- Alert generation only when proposal age exceeds threshold
- Prominent visual warnings in HTML report
- Console output summarizing alerts

**User Experience**
- One-click copy buttons for all Ethereum addresses
- Direct links to view proposals on Snapshot
- Color-coded badges indicating proposal age
- Success message when all members have voted
- Clear visual hierarchy and information architecture

**Automation Support**
- Designed for cron job execution
- Generates static HTML file for easy web serving
- Suitable for scheduled runs (every 24 hours)
- Self-contained execution with minimal dependencies

**Security**
- Environment variable isolation for sensitive configuration
- `.gitignore` configured to exclude `.env` files
- Support for restricted web access via Nginx configuration
- Option for HTTP basic authentication

**Error Handling**
- Graceful API failure handling
- Validation of wallet file existence
- Request timeout configuration (30 seconds)
- Clear error messages for troubleshooting

### Technical Details

**Dependencies**
- Python 3.7+
- `requests==2.31.0` - HTTP library for API calls
- `python-dotenv==1.0.0` - Environment variable management

**API Integration**
- Snapshot GraphQL Hub API endpoint: `https://hub.snapshot.org/graphql`
- Query for active proposals with metadata
- Query for votes on specific proposals
- Voter address normalization (lowercase)

**Data Processing**
- Unix timestamp to human-readable date conversion
- UTC timezone standardization
- Days calculation since proposal creation
- Set operations for efficient voter matching

**Output Format**
- Static HTML5 with embedded CSS and JavaScript
- No external dependencies for viewing
- Works offline once generated
- Printable format

### Known Limitations

- Maximum of 50 proposals fetched per query (Snapshot API limit)
- Maximum of 1000 votes per proposal (Snapshot API limit)
- Requires internet connection to access Snapshot API
- No historical voting data tracking (only current status)

### Deployment Platforms

Tested and documented for:
- Ubuntu 20.04 LTS and newer
- Nginx web server
- systemd or cron for scheduling
- Let's Encrypt for SSL certificates

### File Structure

```
grump/
├── monitor_council_votes.py    # Main monitoring script
├── run_monitor.sh              # Quick start wrapper
├── requirements.txt             # Python dependencies
├── wallets.txt                  # Council member addresses
├── .env                         # Environment configuration
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── README.md                    # User documentation
├── DEPLOY.md                    # Deployment guide
└── CHANGELOG.md                 # This file
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `SNAPSHOT_SPACE` | `council.graphprotocol.eth` | Snapshot space to monitor |
| `ALERT_THRESHOLD_DAYS` | `5` | Days before alerting for non-voters |
| `WALLETS_FILE` | `wallets.txt` | Path to council member addresses |
| `OUTPUT_HTML` | `index.html` | Output HTML report file |

### Future Enhancements

Potential features for future versions:
- Historical voting data tracking
- Email/Slack notifications for alerts
- Multi-space monitoring support
- Vote choice analysis
- Voting pattern analytics
- API endpoint for programmatic access
- Docker containerization
- Database storage for historical trends

---

## Version History

- **[v0.1.1] - 2025-10-28** - Improve dashboard success messages
- **[v0.1.0] - 2025-10-28** - Add dashboard link to Slack messages
- **[v0.0.9] - 2025-10-28** - Add proposal age filtering (PROPOSAL_MAX_AGE_DAYS)
- **[v0.0.8] - 2025-10-28** - Add POST_TO_SLACK toggle for file/Slack output
- **[v0.0.7] - 2025-10-28** - Enhanced proposal title formatting with quotes and dash
- **[v0.0.6] - 2025-10-28** - Remove @ symbol from wallet addresses in Slack messages
- **[v0.0.5] - 2025-10-28** - Slack user mentions (cc) support
- **[v0.0.4] - 2025-10-28** - Slack integration for automated notifications
- **[v0.0.3] - 2025-10-27** - Hide completed proposals feature
- **[v0.0.2] - 2025-10-27** - UI improvements, color-coding, days left counter
- **[v0.0.1] - 2025-10-27** - Initial release

---

[v0.1.1]: https://github.com/pdiomede/grump/releases/tag/v0.1.1
[v0.1.0]: https://github.com/pdiomede/grump/releases/tag/v0.1.0
[v0.0.9]: https://github.com/pdiomede/grump/releases/tag/v0.0.9
[v0.0.8]: https://github.com/pdiomede/grump/releases/tag/v0.0.8
[v0.0.7]: https://github.com/pdiomede/grump/releases/tag/v0.0.7
[v0.0.6]: https://github.com/pdiomede/grump/releases/tag/v0.0.6
[v0.0.5]: https://github.com/pdiomede/grump/releases/tag/v0.0.5
[v0.0.4]: https://github.com/pdiomede/grump/releases/tag/v0.0.4
[v0.0.3]: https://github.com/pdiomede/grump/releases/tag/v0.0.3
[v0.0.2]: https://github.com/pdiomede/grump/releases/tag/v0.0.2
[v0.0.1]: https://github.com/pdiomede/grump/releases/tag/v0.0.1

