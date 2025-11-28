"""Tests for Twitter platform implementation."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from social_scrubber.platforms.twitter import TwitterPlatform

# Use shared fixtures from conftest.py


@pytest.fixture
def twitter_platform(mock_twitter_config):
    """Create a TwitterPlatform instance with mocked config."""
    return TwitterPlatform(mock_twitter_config)


@pytest.fixture
def twitter_platform_unconfigured(mock_twitter_config_unconfigured):
    """Create an unconfigured TwitterPlatform instance."""
    return TwitterPlatform(mock_twitter_config_unconfigured)


class TestTwitterAuthentication:
    """Test cases for Twitter authentication."""

    @pytest.mark.asyncio
    async def test_authenticate_returns_false_wip(self, twitter_platform):
        """Test that authenticate returns False as Twitter is WIP."""
        result = await twitter_platform.authenticate()

        # Twitter integration is WIP, should return False
        assert result is False
        assert twitter_platform.is_authenticated is False


class TestTwitterGetPosts:
    """Test cases for Twitter get_posts method."""

    @pytest.mark.asyncio
    async def test_get_posts_returns_empty_list_wip(self, twitter_platform):
        """Test that get_posts returns empty list as Twitter is WIP."""
        posts = await twitter_platform.get_posts(
            start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 2)
        )

        # Twitter integration is WIP, should return empty list
        assert posts == []


class TestTwitterDeletePost:
    """Test cases for Twitter post deletion."""

    @pytest.mark.asyncio
    async def test_delete_post_returns_not_implemented(self, twitter_platform):
        """Test that delete_post returns failure as Twitter is WIP."""
        result = await twitter_platform.delete_post("test_post_id")

        assert result.success is False
        assert "not yet implemented" in result.error


class TestTwitterPlatformProperties:
    """Test cases for Twitter platform properties."""

    def test_platform_name(self, twitter_platform):
        """Test that platform name is set correctly."""
        assert twitter_platform.name == "twitter"

    def test_display_name(self, twitter_platform):
        """Test that display name is title-cased."""
        assert twitter_platform.display_name == "Twitter"

    def test_is_authenticated_initially_false(self, twitter_platform):
        """Test that is_authenticated is initially False."""
        assert twitter_platform.is_authenticated is False
