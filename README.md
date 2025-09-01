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

1. Clone the repository
2. Create Python virtual environment: `python -m venv .venv` and `source .venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`
4. Copy environment template and update: `cp .env.example .env`
5. Run the tool: `python social-scrubber`
6. Follow the prompts to authenticate and select deletion options

## Configuration

### Environment Variables
```bash
# Bluesky Credentials
BLUESKY_HANDLE=your-handle.bsky.social
BLUESKY_PASSWORD=your-app-password

# Mastodon Credentials  
MASTODON_API_BASE_URL=https://your-instance.social
MASTODON_ACCESS_TOKEN=your-access-token
```

### Key Settings
- `SCRUB_START_DATE`: Date to start deleting posts from (default: 7 days ago)
- `SCRUB_START_END`: End date for posts to stop deleting at (default: today's date)
- `MAX_POSTS_PER_SCRUB`: Maximum scrubs per run (default: 10)
- `DRY_RUN`: Test mode without posting (default: true)

## Disclaimer

Use responsibly! Deleted posts cannot be recovered. This tool is not affiliated with Twitter, Mastodon, or Bluesky.
