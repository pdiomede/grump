# Changelog

All notable changes to The Graph Council Voting Monitor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Configuration
- **Hide Completed Proposals**
  - Added `SHOW_COMPLETED_PROPOSALS` parameter to `.env` file (default: N)
  - When set to "N", proposals with all council members voted (6/6) are hidden from the dashboard
  - When set to "Y", all proposals are displayed regardless of voting completion
  - Helps focus attention on proposals that still need votes
  - Active Proposals counter updates dynamically based on displayed proposals

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

- **[v0.0.2] - 2025-10-27** - UI improvements, color-coding, days left counter
- **[v0.0.1] - 2025-10-27** - Initial release

---

[v0.0.2]: https://github.com/pdiomede/grump/releases/tag/v0.0.2
[v0.0.1]: https://github.com/pdiomede/grump/releases/tag/v0.0.1

