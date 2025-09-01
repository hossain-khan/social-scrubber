"""Mastodon platform implementation."""

import re
from datetime import datetime
from typing import List, Optional

from dateutil import parser as date_parser
from mastodon import Mastodon

from ..config import MastodonConfig
from .base import BasePlatform, DeletionResult, Post


class MastodonPlatform(BasePlatform):
    """Mastodon platform implementation."""

    def __init__(self, config: MastodonConfig):
        """Initialize Mastodon platform.

        Args:
            config: Mastodon configuration
        """
        super().__init__("mastodon")
        self.config = config
        self.client: Optional[Mastodon] = None

    async def authenticate(self) -> bool:
        """Authenticate with Mastodon.

        Returns:
            True if authentication successful, False otherwise.
        """
        if not self.config.is_configured:
            print(
                "❌ Mastodon configuration missing. Please check MASTODON_API_BASE_URL and MASTODON_ACCESS_TOKEN."
            )
            return False

        try:
            self.client = Mastodon(
                access_token=self.config.access_token,
                api_base_url=self.config.api_base_url,
            )

            # Verify credentials
            account = self.client.me()
            self._authenticated = True
            print(
                f"✅ Successfully authenticated with Mastodon as @{account['username']}"
            )
            return True

        except Exception as e:
            print(f"❌ Failed to authenticate with Mastodon: {e}")
            self._authenticated = False
            return False

    async def get_posts(
        self, start_date: datetime, end_date: datetime, limit: Optional[int] = None
    ) -> List[Post]:
        """Retrieve posts from Mastodon within the specified date range.

        Args:
            start_date: Start date for posts to retrieve
            end_date: End date for posts to retrieve
            limit: Maximum number of posts to retrieve

        Returns:
            List of Post objects
        """
        if not self._authenticated or not self.client:
            raise RuntimeError("Not authenticated with Mastodon")

        posts: List[Post] = []
        max_id = None
        collected = 0

        try:
            while True:
                # Get posts from the API
                batch_limit = min(40, limit - collected) if limit else 40
                statuses = self.client.account_statuses(
                    id=self.client.me()["id"],
                    max_id=max_id,
                    limit=batch_limit,
                    only_media=False,
                    exclude_replies=False,
                    exclude_reblogs=True,  # Only get original posts
                )

                if not statuses:
                    break

                for status in statuses:
                    # Parse the created date with proper timezone handling
                    try:
                        created_at = status["created_at"]
                        if isinstance(created_at, str):
                            # Parse string datetime
                            created_at = date_parser.isoparse(created_at)

                        # Convert timezone-aware datetime to UTC, then make naive for comparison
                        if (
                            hasattr(created_at, "tzinfo")
                            and created_at.tzinfo is not None
                        ):
                            created_at = created_at.utctimetuple()
                            created_at = datetime(*created_at[:6])
                        elif hasattr(created_at, "replace"):
                            # If it's timezone-aware, convert to naive UTC
                            created_at = created_at.replace(tzinfo=None)
                    except (ValueError, AttributeError) as e:
                        print(
                            f"Warning: Failed to parse date for status {status['id']}: {e}"
                        )
                        continue

                    # Filter by date range
                    if created_at < start_date or created_at > end_date:
                        if created_at < start_date:
                            # We've gone too far back, stop fetching
                            return posts
                        continue

                    # Extract post content (remove HTML tags)
                    content = re.sub(r"<[^>]+>", "", status["content"])

                    # Create Post object
                    post = Post(
                        id=str(status["id"]),
                        content=content,
                        created_at=created_at,
                        platform=self.name,
                        url=status["url"],
                        metadata={
                            "visibility": status["visibility"],
                            "replies_count": status["replies_count"],
                            "reblogs_count": status["reblogs_count"],
                            "favourites_count": status["favourites_count"],
                        },
                    )

                    posts.append(post)
                    collected += 1

                    if limit and collected >= limit:
                        return posts

                # Update max_id for pagination
                if statuses:
                    max_id = statuses[-1]["id"]
                else:
                    break

            return posts

        except Exception as e:
            print(f"❌ Error retrieving Mastodon posts: {e}")
            return []

    async def delete_post(self, post_id: str) -> DeletionResult:
        """Delete a specific Mastodon post.

        Args:
            post_id: ID of the post to delete

        Returns:
            DeletionResult indicating success/failure and details
        """
        if not self._authenticated or not self.client:
            return DeletionResult(
                post_id=post_id, success=False, error="Not authenticated with Mastodon"
            )

        try:
            # Delete the status
            self.client.status_delete(post_id)

            return DeletionResult(post_id=post_id, success=True)

        except Exception as e:
            return DeletionResult(post_id=post_id, success=False, error=str(e))
