"""Tests for Bluesky platform API fixes."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest

from social_scrubber.config import BlueskyConfig
from social_scrubber.platforms.base import Post
from social_scrubber.platforms.bluesky import BlueskyPlatform


@pytest.fixture
def mock_bluesky_config():
    """Create a mock Bluesky configuration."""
    config = Mock(spec=BlueskyConfig)
    config.handle = "test.bsky.social"
    config.password = "test_password"
    config.is_configured = True
    return config


@pytest.fixture
def bluesky_platform(mock_bluesky_config):
    """Create a BlueskyPlatform instance with mocked config."""
    return BlueskyPlatform(mock_bluesky_config)


class TestBlueskyAPIFixes:
    """Test cases for Bluesky API parameter fixes."""

    @pytest.mark.asyncio
    async def test_get_posts_api_call_with_correct_params(
        self, bluesky_platform, mock_bluesky_config
    ):
        """Test that get_posts calls the API with correct parameter structure."""
        # Mock the client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.feed = []  # Empty feed to end the loop

        # Mock the API method
        mock_client.app.bsky.feed.get_author_feed.return_value = mock_response

        # Set up the platform
        bluesky_platform._authenticated = True
        bluesky_platform.client = mock_client

        # Call get_posts
        _ = await bluesky_platform.get_posts(
            start_date="2024-01-01", end_date="2024-01-02", limit=10
        )  # We don't need the result for this test

        # Verify the API was called with correct parameter structure
        mock_client.app.bsky.feed.get_author_feed.assert_called_once()
        call_args = mock_client.app.bsky.feed.get_author_feed.call_args

        # Check that it was called with a params dict as first argument
        assert len(call_args[0]) == 1  # Should have exactly one positional argument
        params = call_args[0][0]  # The params dict

        # Verify the params structure
        assert isinstance(params, dict)
        assert params["actor"] == "test.bsky.social"
        assert params["limit"] == 10
        assert "cursor" not in params  # No cursor on first call

    @pytest.mark.asyncio
    async def test_get_posts_api_call_with_cursor(
        self, bluesky_platform, mock_bluesky_config
    ):
        """Test that get_posts includes cursor in parameters when paginating."""
        # Mock the client and responses
        mock_client = Mock()

        # First response with cursor
        mock_response1 = Mock()
        mock_feed_item1 = Mock()
        mock_post1 = Mock()
        mock_record1 = Mock()
        mock_record1.created_at = "2024-01-01T12:00:00Z"
        mock_record1.text = "Test post"
        mock_post1.record = mock_record1
        mock_post1.uri = "at://did:plc:test/app.bsky.feed.post/test1"
        mock_post1.cid = "test_cid_1"
        mock_feed_item1.post = mock_post1
        mock_response1.feed = [mock_feed_item1]
        mock_response1.cursor = "test_cursor"

        # Second response without cursor (end of pagination)
        mock_response2 = Mock()
        mock_response2.feed = []

        # Set up the API method to return different responses
        mock_client.app.bsky.feed.get_author_feed.side_effect = [
            mock_response1,
            mock_response2,
        ]

        # Set up the platform
        bluesky_platform._authenticated = True
        bluesky_platform.client = mock_client

        # Call get_posts
        _ = await bluesky_platform.get_posts(
            start_date="2024-01-01", end_date="2024-01-02", limit=100
        )  # We don't need the result for this test

        # Verify the API was called twice
        assert mock_client.app.bsky.feed.get_author_feed.call_count == 2

        # Check first call (no cursor)
        first_call_args = mock_client.app.bsky.feed.get_author_feed.call_args_list[0]
        first_params = first_call_args[0][0]
        assert isinstance(first_params, dict)
        assert first_params["actor"] == "test.bsky.social"
        assert "cursor" not in first_params

        # Check second call (with cursor)
        second_call_args = mock_client.app.bsky.feed.get_author_feed.call_args_list[1]
        second_params = second_call_args[0][0]
        assert isinstance(second_params, dict)
        assert second_params["actor"] == "test.bsky.social"
        assert second_params["cursor"] == "test_cursor"

    @pytest.mark.asyncio
    async def test_get_posts_not_authenticated_raises_error(self, bluesky_platform):
        """Test that get_posts raises error when not authenticated."""
        # Ensure platform is not authenticated
        bluesky_platform._authenticated = False
        bluesky_platform.client = None

        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="Not authenticated with Bluesky"):
            await bluesky_platform.get_posts(
                start_date="2024-01-01", end_date="2024-01-02"
            )

    @pytest.mark.asyncio
    async def test_get_posts_no_client_raises_error(self, bluesky_platform):
        """Test that get_posts raises error when client is None."""
        # Set authenticated but no client
        bluesky_platform._authenticated = True
        bluesky_platform.client = None

        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="Not authenticated with Bluesky"):
            await bluesky_platform.get_posts(
                start_date="2024-01-01", end_date="2024-01-02"
            )

    @pytest.mark.asyncio
    async def test_get_posts_processes_response_correctly(
        self, bluesky_platform, mock_bluesky_config
    ):
        """Test that get_posts correctly processes API response into Post objects."""
        # Mock the client and response
        mock_client = Mock()
        mock_response = Mock()

        # Create a mock feed item
        mock_feed_item = Mock()
        mock_post = Mock()
        mock_record = Mock()
        mock_record.created_at = "2024-01-01T12:00:00.000Z"
        mock_record.text = "Test post content"
        mock_post.record = mock_record
        mock_post.uri = "at://did:plc:test/app.bsky.feed.post/test123"
        mock_post.cid = "test_cid"
        mock_feed_item.post = mock_post

        mock_response.feed = [mock_feed_item]
        mock_client.app.bsky.feed.get_author_feed.return_value = mock_response

        # Set up the platform
        bluesky_platform._authenticated = True
        bluesky_platform.client = mock_client

        # Call get_posts
        posts = await bluesky_platform.get_posts(
            start_date="2024-01-01", end_date="2024-01-02"
        )

        # Verify we got one post
        assert len(posts) == 1

        # Verify the post properties
        post = posts[0]
        assert isinstance(post, Post)
        assert post.id == "test123"  # Should extract the ID from the URI
        assert post.text == "Test post content"
        assert post.platform == "bluesky"
        assert isinstance(post.created_at, datetime)

    @pytest.mark.asyncio
    async def test_get_posts_handles_empty_response(
        self, bluesky_platform, mock_bluesky_config
    ):
        """Test that get_posts handles empty API response correctly."""
        # Mock the client and empty response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.feed = []
        mock_client.app.bsky.feed.get_author_feed.return_value = mock_response

        # Set up the platform
        bluesky_platform._authenticated = True
        bluesky_platform.client = mock_client

        # Call get_posts
        posts = await bluesky_platform.get_posts(
            start_date="2024-01-01", end_date="2024-01-02"
        )

        # Verify we got no posts
        assert len(posts) == 0

    @pytest.mark.asyncio
    async def test_get_posts_respects_limit_parameter(
        self, bluesky_platform, mock_bluesky_config
    ):
        """Test that get_posts respects the limit parameter in API calls."""
        # Mock the client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.feed = []
        mock_client.app.bsky.feed.get_author_feed.return_value = mock_response

        # Set up the platform
        bluesky_platform._authenticated = True
        bluesky_platform.client = mock_client

        # Call get_posts with specific limit
        await bluesky_platform.get_posts(
            start_date="2024-01-01", end_date="2024-01-02", limit=25
        )

        # Verify the API was called with correct limit
        call_args = mock_client.app.bsky.feed.get_author_feed.call_args
        params = call_args[0][0]
        assert params["limit"] == 25

    @pytest.mark.asyncio
    async def test_get_posts_handles_api_exception(
        self, bluesky_platform, mock_bluesky_config
    ):
        """Test that get_posts properly handles API exceptions."""
        # Mock the client to raise an exception
        mock_client = Mock()
        mock_client.app.bsky.feed.get_author_feed.side_effect = Exception("API Error")

        # Set up the platform
        bluesky_platform._authenticated = True
        bluesky_platform.client = mock_client

        # Should raise the exception
        with pytest.raises(Exception, match="API Error"):
            await bluesky_platform.get_posts(
                start_date="2024-01-01", end_date="2024-01-02"
            )
