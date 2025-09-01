"""Main CLI application for Social Scrubber."""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

import click
from rich.console import Console

from .config import Config
from .platforms.base import BasePlatform
from .platforms.bluesky import BlueskyPlatform
from .platforms.mastodon import MastodonPlatform
from .platforms.twitter import TwitterPlatform
from .utils import (
    confirm_action,
    display_deletion_results,
    display_posts_table,
    ensure_archive_directory,
    format_date_range,
    print_banner,
    print_platform_status,
    setup_logging,
)

console = Console()


class SocialScrubber:
    """Main Social Scrubber application."""

    def __init__(self):
        """Initialize the Social Scrubber."""
        self.config = Config.from_env()
        setup_logging(self.config.log_level)

        # Initialize platforms
        self.platforms: Dict[str, BasePlatform] = {
            "bluesky": BlueskyPlatform(self.config.bluesky),
            "mastodon": MastodonPlatform(self.config.mastodon),
            "twitter": TwitterPlatform(self.config.twitter),
        }

    async def authenticate_platforms(
        self, selected_platforms: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """Authenticate with selected platforms.

        Args:
            selected_platforms: List of platform names to authenticate with.
                               If None, tries to authenticate with all configured platforms.

        Returns:
            Dictionary mapping platform names to authentication success status.
        """
        auth_results = {}

        platforms_to_auth = (
            selected_platforms if selected_platforms else list(self.platforms.keys())
        )

        for platform_name in platforms_to_auth:
            if platform_name not in self.platforms:
                continue

            platform = self.platforms[platform_name]
            console.print(f"\n🔐 Authenticating with {platform.display_name}...")

            success = await platform.authenticate()
            auth_results[platform_name] = success

        return auth_results

    async def get_posts_from_platforms(
        self,
        platform_names: List[str],
        start_date: datetime,
        end_date: datetime,
        limit: Optional[int] = None,
    ) -> Dict[str, List]:
        """Get posts from specified platforms.

        Args:
            platform_names: List of platform names
            start_date: Start date for posts
            end_date: End date for posts
            limit: Maximum posts per platform

        Returns:
            Dictionary mapping platform names to lists of posts
        """
        all_posts = {}

        for platform_name in platform_names:
            platform = self.platforms[platform_name]

            if not platform.is_authenticated:
                console.print(f"⚠️ Skipping {platform.display_name} - not authenticated")
                continue

            console.print(f"📥 Fetching posts from {platform.display_name}...")

            try:
                posts = await platform.get_posts(start_date, end_date, limit)
                all_posts[platform_name] = posts

                if posts:
                    console.print(
                        f"✅ Found {len(posts)} posts from {platform.display_name}"
                    )
                else:
                    console.print(
                        f"ℹ️ No posts found from {platform.display_name} in date range"
                    )

            except Exception as e:
                console.print(
                    f"❌ Error fetching posts from {platform.display_name}: {e}"
                )
                all_posts[platform_name] = []

        return all_posts

    async def delete_posts_from_platform(
        self, platform_name: str, posts: List, dry_run: bool = True
    ) -> List:
        """Delete posts from a specific platform.

        Args:
            platform_name: Name of the platform
            posts: List of posts to delete
            dry_run: Whether to perform a dry run

        Returns:
            List of deletion results
        """
        platform = self.platforms[platform_name]

        if not posts:
            return []

        if dry_run:
            console.print(
                f"🔍 [DRY RUN] Would delete {len(posts)} posts from {platform.display_name}"
            )
            return []

        console.print(f"🗑️ Deleting {len(posts)} posts from {platform.display_name}...")

        # Ensure archive directory exists if archiving is enabled
        if self.config.scrub.archive_before_delete:
            if not ensure_archive_directory(self.config.scrub.archive_path):
                console.print(
                    "❌ Failed to create archive directory. Aborting deletion."
                )
                return []

        # Perform bulk deletion
        results = await platform.bulk_delete_posts(
            posts,
            archive_before_delete=self.config.scrub.archive_before_delete,
            archive_path=self.config.scrub.archive_path,
        )

        return results

    async def run_interactive(self):
        """Run the interactive mode."""
        print_banner()

        console.print("🔧 Checking platform configurations...")

        # Display platform status
        for platform_name, platform in self.platforms.items():
            config_attr = getattr(self.config, platform_name)
            print_platform_status(
                platform_name, config_attr.is_configured, platform.is_authenticated
            )

        # Get configured platforms
        configured_platforms = [
            name
            for name, platform in self.platforms.items()
            if getattr(self.config, name).is_configured
        ]

        if not configured_platforms:
            console.print(
                "\n❌ No platforms are configured. Please check your .env file."
            )
            return

        # Authenticate with platforms
        console.print(
            f"\n🔐 Authenticating with {len(configured_platforms)} platform(s)..."
        )
        auth_results = await self.authenticate_platforms(configured_platforms)

        authenticated_platforms = [
            name for name, success in auth_results.items() if success
        ]

        if not authenticated_platforms:
            console.print("\n❌ Failed to authenticate with any platforms.")
            return

        # Get date range
        start_date = self.config.scrub.get_start_datetime()
        end_date = self.config.scrub.get_end_datetime()

        console.print(f"\n📅 Date range: {format_date_range(start_date, end_date)}")
        console.print(
            f"🔢 Max posts per platform: {self.config.scrub.max_posts_per_scrub}"
        )
        console.print(
            f"🧪 Dry run mode: {'ON' if self.config.scrub.dry_run else 'OFF'}"
        )

        if not confirm_action("Proceed with fetching posts?", default=True):
            console.print("Operation cancelled.")
            return

        # Fetch posts from all authenticated platforms
        all_posts = await self.get_posts_from_platforms(
            authenticated_platforms,
            start_date,
            end_date,
            self.config.scrub.max_posts_per_scrub,
        )

        # Display posts found
        total_posts = sum(len(posts) for posts in all_posts.values())
        if total_posts == 0:
            console.print("\n✅ No posts found in the specified date range.")
            return

        console.print(f"\n📊 Found {total_posts} posts total:")
        for platform_name, posts in all_posts.items():
            if posts:
                display_posts_table(posts, f"{platform_name.title()} Posts")

        # Confirm deletion
        if self.config.scrub.dry_run:
            console.print("\n🧪 This is a DRY RUN. No posts will actually be deleted.")
        else:
            if not confirm_action(f"Delete {total_posts} posts?", default=False):
                console.print("Deletion cancelled.")
                return

        # Delete posts from each platform
        for platform_name, posts in all_posts.items():
            if not posts:
                continue

            results = await self.delete_posts_from_platform(
                platform_name, posts, dry_run=self.config.scrub.dry_run
            )

            if results:
                display_deletion_results(results, platform_name)

        console.print("\n✅ Social Scrubber completed!")


@click.command()
@click.option(
    "--dry-run/--no-dry-run",
    default=None,
    help="Enable or disable dry run mode (overrides config)",
)
@click.option(
    "--max-posts",
    type=int,
    default=None,
    help="Maximum posts to process per platform (overrides config)",
)
@click.option(
    "--platforms",
    default=None,
    help="Comma-separated list of platforms to process (bluesky,mastodon,twitter)",
)
@click.option(
    "--start-date",
    default=None,
    help='Start date in ISO format (YYYY-MM-DD) or "7_days_ago" (overrides config)',
)
@click.option(
    "--end-date",
    default=None,
    help='End date in ISO format (YYYY-MM-DD) or "today" (overrides config)',
)
def main(dry_run, max_posts, platforms, start_date, end_date):
    """Social Scrubber - Bulk delete your social media posts."""

    # Create and configure the scrubber
    scrubber = SocialScrubber()

    # Override config with CLI arguments
    if dry_run is not None:
        scrubber.config.scrub.dry_run = dry_run

    if max_posts is not None:
        scrubber.config.scrub.max_posts_per_scrub = max_posts

    if start_date is not None:
        scrubber.config.scrub.start_date = start_date

    if end_date is not None:
        scrubber.config.scrub.end_date = end_date

    # Run the interactive scrubber
    asyncio.run(scrubber.run_interactive())


if __name__ == "__main__":
    main()
