# Changelog

All notable changes to The Graph Council Voting Monitor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- **[v0.0.1] - 2025-10-27** - Initial release

---

[v0.0.1]: https://github.com/yourusername/grump/releases/tag/v0.0.1

