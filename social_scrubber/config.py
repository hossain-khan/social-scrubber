"""Configuration management for Social Scrubber."""

import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class BlueskyConfig(BaseModel):
    """Bluesky configuration."""

    handle: str = Field(default="", description="Bluesky handle")
    password: str = Field(default="", description="Bluesky app password")

    @property
    def is_configured(self) -> bool:
        """Check if Bluesky is properly configured."""
        return bool(self.handle and self.password)


class MastodonConfig(BaseModel):
    """Mastodon configuration."""

    api_base_url: str = Field(default="", description="Mastodon instance URL")
    access_token: str = Field(default="", description="Mastodon access token")

    @property
    def is_configured(self) -> bool:
        """Check if Mastodon is properly configured."""
        return bool(self.api_base_url and self.access_token)


class TwitterConfig(BaseModel):
    """Twitter/X configuration."""

    api_key: str = Field(default="", description="Twitter API key")
    api_secret: str = Field(default="", description="Twitter API secret")
    access_token: str = Field(default="", description="Twitter access token")
    access_token_secret: str = Field(
        default="", description="Twitter access token secret"
    )
    bearer_token: str = Field(default="", description="Twitter bearer token")

    @property
    def is_configured(self) -> bool:
        """Check if Twitter is properly configured."""
        return bool(
            self.api_key
            and self.api_secret
            and self.access_token
            and self.access_token_secret
        )


class ScrubConfig(BaseModel):
    """Scrubbing configuration."""

    start_date: str = Field(
        default="7_days_ago", description="Start date for scrubbing"
    )
    end_date: str = Field(default="today", description="End date for scrubbing")
    max_posts_per_scrub: int = Field(
        default=10, description="Maximum posts to scrub per run"
    )
    dry_run: bool = Field(default=True, description="Whether to run in dry-run mode")
    archive_before_delete: bool = Field(
        default=True, description="Archive posts before deletion"
    )
    archive_path: str = Field(
        default="./archives", description="Path to store archives"
    )

    def get_start_datetime(self) -> datetime:
        """Parse start date into datetime object."""
        if self.start_date == "7_days_ago":
            return datetime.now() - timedelta(days=7)
        elif self.start_date == "today":
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Try to parse as ISO format
            try:
                return datetime.fromisoformat(self.start_date)
            except ValueError:
                raise ValueError(f"Invalid start date format: {self.start_date}")

    def get_end_datetime(self) -> datetime:
        """Parse end date into datetime object."""
        if self.end_date == "today":
            return datetime.now()
        else:
            # Try to parse as ISO format
            try:
                return datetime.fromisoformat(self.end_date)
            except ValueError:
                raise ValueError(f"Invalid end date format: {self.end_date}")


class Config(BaseModel):
    """Main configuration class."""

    bluesky: BlueskyConfig
    mastodon: MastodonConfig
    twitter: TwitterConfig
    scrub: ScrubConfig
    log_level: str = Field(default="INFO", description="Logging level")

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            bluesky=BlueskyConfig(
                handle=os.getenv("BLUESKY_HANDLE", ""),
                password=os.getenv("BLUESKY_PASSWORD", ""),
            ),
            mastodon=MastodonConfig(
                api_base_url=os.getenv("MASTODON_API_BASE_URL", ""),
                access_token=os.getenv("MASTODON_ACCESS_TOKEN", ""),
            ),
            twitter=TwitterConfig(
                api_key=os.getenv("TWITTER_API_KEY", ""),
                api_secret=os.getenv("TWITTER_API_SECRET", ""),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN", ""),
                access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN", ""),
            ),
            scrub=ScrubConfig(
                start_date=os.getenv("SCRUB_START_DATE", "7_days_ago"),
                end_date=os.getenv("SCRUB_END_DATE", "today"),
                max_posts_per_scrub=int(os.getenv("MAX_POSTS_PER_SCRUB", "10")),
                dry_run=os.getenv("DRY_RUN", "true").lower() == "true",
                archive_before_delete=os.getenv("ARCHIVE_BEFORE_DELETE", "true").lower()
                == "true",
                archive_path=os.getenv("ARCHIVE_PATH", "./archives"),
            ),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
