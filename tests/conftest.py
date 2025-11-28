"""Shared test configuration and fixtures."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from social_scrubber.config import BlueskyConfig, MastodonConfig, TwitterConfig
from social_scrubber.platforms.base import DeletionResult, Post


@pytest.fixture
def sample_post():
    """Create a sample post for testing."""
    return Post(
        id="test_post_123",
        content="Test content for the post",
        created_at=datetime(2024, 1, 15, 10, 30),
        platform="test",
        url="https://example.com/post/test_post_123",
        metadata={"key": "value"},
    )


@pytest.fixture
def sample_posts():
    """Create a list of sample posts for testing."""
    return [
        Post(
            id="post1",
            content="First post content",
            created_at=datetime(2024, 1, 15, 10, 30),
            platform="test",
        ),
        Post(
            id="post2",
            content="Second post content",
            created_at=datetime(2024, 1, 16, 12, 0),
            platform="test",
        ),
    ]


@pytest.fixture
def sample_deletion_results():
    """Create sample deletion results for testing."""
    return [
        DeletionResult(post_id="post1", success=True, archived=True),
        DeletionResult(post_id="post2", success=True, archived=False),
        DeletionResult(post_id="post3", success=False, error="Network error"),
    ]


# Bluesky fixtures
@pytest.fixture
def mock_bluesky_config():
    """Create a mock Bluesky configuration."""
    config = Mock(spec=BlueskyConfig)
    config.handle = "test.bsky.social"
    config.password = "test_password"
    config.is_configured = True
    return config


@pytest.fixture
def mock_bluesky_config_unconfigured():
    """Create a mock unconfigured Bluesky configuration."""
    config = Mock(spec=BlueskyConfig)
    config.handle = ""
    config.password = ""
    config.is_configured = False
    return config


# Mastodon fixtures
@pytest.fixture
def mock_mastodon_config():
    """Create a mock Mastodon configuration."""
    config = Mock(spec=MastodonConfig)
    config.api_base_url = "https://mastodon.social"
    config.access_token = "test_access_token"
    config.is_configured = True
    return config


@pytest.fixture
def mock_mastodon_config_unconfigured():
    """Create a mock unconfigured Mastodon configuration."""
    config = Mock(spec=MastodonConfig)
    config.api_base_url = ""
    config.access_token = ""
    config.is_configured = False
    return config


# Twitter fixtures
@pytest.fixture
def mock_twitter_config():
    """Create a mock Twitter configuration."""
    config = Mock(spec=TwitterConfig)
    config.api_key = "test_api_key"
    config.api_secret = "test_api_secret"
    config.access_token = "test_access_token"
    config.access_token_secret = "test_access_token_secret"
    config.bearer_token = "test_bearer_token"
    config.is_configured = True
    return config


@pytest.fixture
def mock_twitter_config_unconfigured():
    """Create a mock unconfigured Twitter configuration."""
    config = Mock(spec=TwitterConfig)
    config.api_key = ""
    config.api_secret = ""
    config.access_token = ""
    config.access_token_secret = ""
    config.bearer_token = ""
    config.is_configured = False
    return config
