"""Test configuration module."""

import os
from datetime import datetime, timedelta

import pytest

from social_scrubber.config import BlueskyConfig, Config, MastodonConfig, ScrubConfig


class TestConfig:
    """Test configuration classes."""

    def test_scrub_config_default_dates(self):
        """Test default date parsing in ScrubConfig."""
        config = ScrubConfig()

        # Test default start date (7 days ago)
        start_date = config.get_start_datetime()
        expected_start = datetime.now() - timedelta(days=7)

        # Allow for some time difference in test execution
        assert abs((start_date - expected_start).total_seconds()) < 60

        # Test default end date (today)
        end_date = config.get_end_datetime()
        expected_end = datetime.now()

        # Allow for some time difference in test execution
        assert abs((end_date - expected_end).total_seconds()) < 60

    def test_scrub_config_custom_dates(self):
        """Test custom date parsing in ScrubConfig."""
        config = ScrubConfig(
            start_date="2024-01-01T00:00:00", end_date="2024-01-31T23:59:59"
        )

        start_date = config.get_start_datetime()
        end_date = config.get_end_datetime()

        assert start_date.year == 2024
        assert start_date.month == 1
        assert start_date.day == 1

        assert end_date.year == 2024
        assert end_date.month == 1
        assert end_date.day == 31

    def test_bluesky_config_validation(self):
        """Test BlueskyConfig validation."""
        # Empty config should not be configured
        config = BlueskyConfig()
        assert not config.is_configured

        # Partial config should not be configured
        config = BlueskyConfig(handle="test.bsky.social", password="")
        assert not config.is_configured

        # Full config should be configured
        config = BlueskyConfig(handle="test.bsky.social", password="test-password")
        assert config.is_configured

    def test_mastodon_config_validation(self):
        """Test MastodonConfig validation."""
        # Empty config should not be configured
        config = MastodonConfig()
        assert not config.is_configured

        # Partial config should not be configured
        config = MastodonConfig(api_base_url="https://mastodon.social", access_token="")
        assert not config.is_configured

        # Full config should be configured
        config = MastodonConfig(
            api_base_url="https://mastodon.social", access_token="test-token"
        )
        assert config.is_configured

    def test_config_from_env(self, monkeypatch):
        """Test Config.from_env() method."""
        # Set some environment variables using monkeypatch for automatic cleanup
        monkeypatch.setenv("BLUESKY_HANDLE", "test.bsky.social")
        monkeypatch.setenv("BLUESKY_PASSWORD", "test-password")
        monkeypatch.setenv("DRY_RUN", "false")
        monkeypatch.setenv("MAX_POSTS_PER_SCRUB", "25")

        config = Config.from_env()

        assert config.bluesky.handle == "test.bsky.social"
        assert config.bluesky.password == "test-password"
        assert config.scrub.dry_run is False
        assert config.scrub.max_posts_per_scrub == 25

        # No manual cleanup needed - monkeypatch handles it automatically
