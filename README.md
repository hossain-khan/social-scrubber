# social-scrubber
**Social Scrubber** is a Python tool to help you bulk-delete your posts from Twitter, Mastodon, and Bluesky. Whether you want to clear out old tweets, toots, or skeets from a specific period or just clean up your timeline, SocialCleaner provides a simple and unified interface for secure, automated deletion.


## Features

- Bulk-delete posts from Twitter, Mastodon, and Bluesky (🚧 WIP 🚧)
- Filter deletions by date or keyword or post ids
- Dry-run mode to preview posts before deletion
- Option to archive post before deletion
- Cross-platform support (Windows, macOS, Linux)
- Easy authentication via access tokens

## Getting Started

### Quick Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/hossain-khan/social-scrubber.git
   cd social-scrubber
   ```

2. Set up the development environment:
   ```bash
   make setup
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\activate     # Windows
   ```

4. Install dependencies:
   ```bash
   make install
   ```

5. Configure your credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your platform credentials
   ```

6. Run the tool:
   ```bash
   make run
   # or
   social-scrubber
   # or
   python -m social_scrubber
   ```

### Manual Setup
If you prefer not to use Make:

1. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment template and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. Run the tool:
   ```bash
   social-scrubber
   ```

## Configuration

### Platform Credentials

#### Bluesky
1. Go to your Bluesky Settings > App Passwords
2. Create a new app password
3. Add to your `.env` file:
   ```bash
   BLUESKY_HANDLE=your-handle.bsky.social
   BLUESKY_PASSWORD=your-app-password
   ```

#### Mastodon
1. Go to your Mastodon instance Settings > Development > Applications
2. Create a new application with `read` and `write` scopes
3. Copy the access token
4. Add to your `.env` file:
   ```bash
   MASTODON_API_BASE_URL=https://your-instance.social
   MASTODON_ACCESS_TOKEN=your-access-token
   ```

#### Twitter/X (Coming Soon)
Twitter integration is planned but not yet implemented.

### Environment Variables
```bash
# Bluesky Credentials
BLUESKY_HANDLE=your-handle.bsky.social
BLUESKY_PASSWORD=your-app-password

# Mastodon Credentials  
MASTODON_API_BASE_URL=https://your-instance.social
MASTODON_ACCESS_TOKEN=your-access-token

# Twitter/X Credentials (Future use)
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
TWITTER_BEARER_TOKEN=your-bearer-token

# Scrub Configuration
SCRUB_START_DATE=7_days_ago  # or ISO date like 2024-01-01T00:00:00
SCRUB_END_DATE=today         # or ISO date like 2024-01-31T23:59:59
MAX_POSTS_PER_SCRUB=10       # Maximum posts to process per platform
DRY_RUN=true                 # Set to 'false' to actually delete posts

# Archival Settings
ARCHIVE_BEFORE_DELETE=true   # Archive posts before deletion
ARCHIVE_PATH=./archives      # Where to store archived posts

# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
```

## Usage

### Interactive Mode (Recommended)
Run the tool in interactive mode for a guided experience:

```bash
social-scrubber
```

The interactive mode will:
1. Check your platform configurations
2. Authenticate with configured platforms
3. Show you posts that would be deleted
4. Ask for confirmation before deletion
5. Display results and archive information

### CLI Commands
Social Scrubber provides several commands for different operations:

#### Main Commands
```bash
# Show all available commands and options
social-scrubber --help

# Show version information
social-scrubber --version

# Show current configuration
social-scrubber config

# Test platform connections without scrubbing
social-scrubber test

# Run the scrub process (default command)
social-scrubber scrub [OPTIONS]
```

#### Scrub Command Options
The `scrub` command (which runs by default) supports these options:

```bash
# Run in dry-run mode (safe - won't actually delete)
social-scrubber scrub --dry-run
# OR (backward compatible)
social-scrubber --dry-run

# Actually delete posts (be careful!)
social-scrubber scrub --no-dry-run

# Process only specific platforms
social-scrubber scrub --platforms bluesky,mastodon

# Limit number of posts per platform
social-scrubber scrub --max-posts 5

# Custom date range
social-scrubber scrub --start-date 2024-01-01T00:00:00 --end-date 2024-01-31T23:59:59

# Set logging level for detailed output
social-scrubber --log-level DEBUG scrub --dry-run
```

#### Quick Examples
```bash
# Check your configuration
social-scrubber config

# Test if your platform credentials work
social-scrubber test

# Safely preview what would be deleted
social-scrubber --dry-run

# Actually delete posts (with confirmation)
social-scrubber --no-dry-run

# Debug connection issues
social-scrubber --log-level DEBUG test
```

> **Note**: You can also use `python -m social_scrubber` if you prefer the module syntax.

### Development Commands
If you're developing or contributing:

```bash
# Set up development environment
make setup
make install-dev

# Run all pre-commit quality checks
make pre-commit

# Individual quality checks
make format    # Format code (black + isort)
make lint      # Run linting (flake8 + mypy + bandit)
make test      # Run test suite

# Pre-commit hooks (optional but recommended)
pre-commit install
pre-commit run --all-files

# Manual script execution
./scripts/pre-commit-checks.sh

# Clean build artifacts
make clean
```

## Project Structure

```
social-scrubber/
├── social_scrubber/           # Main package
│   ├── __init__.py           # Package info
│   ├── __main__.py           # Entry point for -m flag
│   ├── cli.py                # Command-line interface
│   ├── config.py             # Configuration management
│   ├── utils.py              # Utility functions
│   └── platforms/            # Platform implementations
│       ├── __init__.py
│       ├── base.py           # Base platform interface
│       ├── bluesky.py        # Bluesky implementation
│       ├── mastodon.py       # Mastodon implementation
│       └── twitter.py        # Twitter implementation (WIP)
├── tests/                    # Test suite
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup
├── Makefile                # Development commands
├── social-scrubber         # Executable script
└── README.md               # This file
```

## Safety Features

- **Dry Run Mode**: Enabled by default - see what would be deleted without actually deleting
- **Date Filtering**: Only delete posts within specified date ranges
- **Post Limits**: Configurable maximum posts per run to prevent accidents
- **Archival**: Automatically archive posts before deletion (configurable)
- **Confirmation Prompts**: Interactive confirmation before destructive actions
- **Detailed Logging**: Comprehensive logs of all operations

## Supported Platforms

| Platform | Status | Features |
|----------|--------|----------|
| **Bluesky** | ✅ Working | Full CRUD operations, date filtering, archival |
| **Mastodon** | ✅ Working | Full CRUD operations, date filtering, archival |
| **Twitter/X** | 🚧 Planned | Coming in future release |

## CI/CD & Quality Assurance

### Automated Checks
This project uses comprehensive CI/CD pipelines to ensure code quality:

- **🔍 Code Quality**: Black formatting, isort imports, flake8 linting, mypy type checking
- **🔒 Security**: Bandit security scanning, dependency vulnerability checks  
- **🧪 Testing**: Full test suite across Python 3.8-3.12 on Linux, Windows, macOS
- **📦 Build**: Package installation and executable testing
- **🚀 Release**: Automated PyPI publishing on tagged releases

### GitHub Actions Workflows
- **CI Pipeline** (`.github/workflows/ci.yml`): Runs on every push and PR
- **Release Pipeline** (`.github/workflows/release.yml`): Automated package publishing
- **Dependency Updates** (`.github/workflows/dependencies.yml`): Weekly security and update checks

### Pre-commit Hooks
Install pre-commit hooks for local development:
```bash
pip install pre-commit
pre-commit install
```

Run quality checks before committing:
```bash
make pre-commit  # or ./scripts/pre-commit-checks.sh
```

## Disclaimer

Use responsibly! Deleted posts cannot be recovered. This tool is not affiliated with Twitter, Mastodon, or Bluesky.
