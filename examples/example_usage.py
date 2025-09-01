#!/usr/bin/env python3
"""
Example script showing how to use Social Scrubber programmatically.

This script demonstrates how to:
1. Configure the scrubber
2. Authenticate with platforms
3. Fetch posts from a date range
4. Preview posts before deletion
5. Perform deletion with archival
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to Python path to import social_scrubber
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from social_scrubber.config import Config
from social_scrubber.platforms.bluesky import BlueskyPlatform
from social_scrubber.platforms.mastodon import MastodonPlatform
from social_scrubber.utils import display_posts_table, display_deletion_results


async def main():
    """Main example function."""
    print("🧪 Social Scrubber Example Script")
    print("=" * 40)
    
    # Load configuration
    config = Config.from_env()
    
    # Calculate date range (last 3 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    print(f"📅 Looking for posts from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Initialize platforms
    platforms = []
    
    # Add Bluesky if configured
    if config.bluesky.is_configured:
        platforms.append(('bluesky', BlueskyPlatform(config.bluesky)))
    
    # Add Mastodon if configured
    if config.mastodon.is_configured:
        platforms.append(('mastodon', MastodonPlatform(config.mastodon)))
    
    if not platforms:
        print("❌ No platforms configured. Please set up your .env file.")
        return
    
    # Authenticate with platforms
    for platform_name, platform in platforms:
        print(f"\n🔐 Authenticating with {platform_name.title()}...")
        success = await platform.authenticate()
        
        if not success:
            print(f"❌ Failed to authenticate with {platform_name}")
            continue
        
        # Fetch posts
        print(f"📥 Fetching posts from {platform_name.title()}...")
        posts = await platform.get_posts(
            start_date=start_date,
            end_date=end_date,
            limit=5  # Limit to 5 posts for this example
        )
        
        if posts:
            print(f"✅ Found {len(posts)} posts")
            display_posts_table(posts, f"{platform_name.title()} Posts")
            
            # Example: Preview what would be deleted (dry run)
            print(f"\n🔍 This is what would be deleted from {platform_name.title()}:")
            for post in posts:
                print(f"  • {post}")
            
            # Note: In a real scenario, you would ask for user confirmation
            # before proceeding with actual deletion
            print(f"\n💡 To actually delete these posts, set DRY_RUN=false in your .env file")
            
        else:
            print(f"ℹ️ No posts found in the specified date range")
    
    print("\n✅ Example script completed!")


if __name__ == '__main__':
    asyncio.run(main())
