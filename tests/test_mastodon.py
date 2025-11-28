"""Tests for Mastodon platform implementation."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from social_scrubber.platforms.base import Post
from social_scrubber.platforms.mastodon import MastodonPlatform

# Use shared fixtures from conftest.py


@pytest.fixture
def mastodon_platform(mock_mastodon_config):
    """Create a MastodonPlatform instance with mocked config."""
    return MastodonPlatform(mock_mastodon_config)


@pytest.fixture
def mastodon_platform_unconfigured(mock_mastodon_config_unconfigured):
    """Create an unconfigured MastodonPlatform instance."""
    return MastodonPlatform(mock_mastodon_config_unconfigured)


class TestMastodonAuthentication:
    """Test cases for Mastodon authentication."""

    @pytest.mark.asyncio
    async def test_authenticate_success(self, mastodon_platform, mock_mastodon_config):
        """Test successful authentication with Mastodon."""
        with patch("social_scrubber.platforms.mastodon.Mastodon") as MockMastodon:
            mock_client = Mock()
            mock_client.me.return_value = {"username": "testuser"}
            MockMastodon.return_value = mock_client

            result = await mastodon_platform.authenticate()

            assert result is True
            assert mastodon_platform.is_authenticated is True
            MockMastodon.assert_called_once_with(
                access_token="test_access_token",
                api_base_url="https://mastodon.social",
            )

    @pytest.mark.asyncio
    async def test_authenticate_failure(self, mastodon_platform, mock_mastodon_config):
        """Test failed authentication with Mastodon."""
        with patch("social_scrubber.platforms.mastodon.Mastodon") as MockMastodon:
            mock_client = Mock()
            mock_client.me.side_effect = Exception("Invalid token")
            MockMastodon.return_value = mock_client

            result = await mastodon_platform.authenticate()

            assert result is False
            assert mastodon_platform.is_authenticated is False

    @pytest.mark.asyncio
    async def test_authenticate_not_configured(self, mastodon_platform_unconfigured):
        """Test authentication fails when not configured."""
        result = await mastodon_platform_unconfigured.authenticate()

        assert result is False
        assert mastodon_platform_unconfigured.is_authenticated is False


class TestMastodonGetPosts:
    """Test cases for Mastodon get_posts method."""

    @pytest.mark.asyncio
    async def test_get_posts_not_authenticated_raises_error(self, mastodon_platform):
        """Test that get_posts raises error when not authenticated."""
        mastodon_platform._authenticated = False
        mastodon_platform.client = None

        with pytest.raises(RuntimeError, match="Not authenticated with Mastodon"):
            await mastodon_platform.get_posts(
                start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 2)
            )

    @pytest.mark.asyncio
    async def test_get_posts_empty_response(
        self, mastodon_platform, mock_mastodon_config
    ):
        """Test that get_posts handles empty API response."""
        mock_client = Mock()
        mock_client.me.return_value = {"id": "123456"}
        mock_client.account_statuses.return_value = []

        mastodon_platform._authenticated = True
        mastodon_platform.client = mock_client

        posts = await mastodon_platform.get_posts(
            start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 2)
        )

        assert len(posts) == 0

    @pytest.mark.asyncio
    async def test_get_posts_processes_response(
        self, mastodon_platform, mock_mastodon_config
    ):
        """Test that get_posts correctly processes API response."""
        mock_client = Mock()
        mock_client.me.return_value = {"id": "123456"}

        mock_status = {
            "id": "status123",
            "created_at": "2024-01-15T10:30:00Z",
            "content": "<p>Test post content</p>",
            "url": "https://mastodon.social/@test/status123",
            "visibility": "public",
            "replies_count": 5,
            "reblogs_count": 10,
            "favourites_count": 20,
        }
        # First call returns statuses, second call returns empty to end pagination
        mock_client.account_statuses.side_effect = [[mock_status], []]

        mastodon_platform._authenticated = True
        mastodon_platform.client = mock_client

        posts = await mastodon_platform.get_posts(
            start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 31)
        )

        assert len(posts) == 1
        post = posts[0]
        assert isinstance(post, Post)
        assert post.id == "status123"
        assert "Test post content" in post.content
        assert post.platform == "mastodon"

    @pytest.mark.asyncio
    async def test_get_posts_respects_limit(
        self, mastodon_platform, mock_mastodon_config
    ):
        """Test that get_posts respects the limit parameter."""
        mock_client = Mock()
        mock_client.me.return_value = {"id": "123456"}

        mock_statuses = [
            {
                "id": f"status{i}",
                "created_at": f"2024-01-{15+i:02d}T10:30:00Z",
                "content": f"<p>Post {i}</p>",
                "url": f"https://mastodon.social/@test/status{i}",
                "visibility": "public",
                "replies_count": 0,
                "reblogs_count": 0,
                "favourites_count": 0,
            }
            for i in range(5)
        ]
        mock_client.account_statuses.return_value = mock_statuses

        mastodon_platform._authenticated = True
        mastodon_platform.client = mock_client

        posts = await mastodon_platform.get_posts(
            start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 31), limit=3
        )

        # Should get at most 3 posts due to limit
        assert len(posts) <= 3

    @pytest.mark.asyncio
    async def test_get_posts_filters_by_date_range(
        self, mastodon_platform, mock_mastodon_config
    ):
        """Test that get_posts filters posts by date range."""
        mock_client = Mock()
        mock_client.me.return_value = {"id": "123456"}

        # Posts returned in reverse chronological order (newest first)
        mock_statuses = [
            {
                "id": "status1",
                "created_at": "2024-01-25T10:30:00Z",  # After range
                "content": "<p>After range</p>",
                "url": "https://mastodon.social/@test/status1",
                "visibility": "public",
                "replies_count": 0,
                "reblogs_count": 0,
                "favourites_count": 0,
            },
            {
                "id": "status2",
                "created_at": "2024-01-15T10:30:00Z",  # In range
                "content": "<p>In range</p>",
                "url": "https://mastodon.social/@test/status2",
                "visibility": "public",
                "replies_count": 0,
                "reblogs_count": 0,
                "favourites_count": 0,
            },
            {
                "id": "status3",
                "created_at": "2024-01-05T10:30:00Z",  # Before range - will stop here
                "content": "<p>Before range</p>",
                "url": "https://mastodon.social/@test/status3",
                "visibility": "public",
                "replies_count": 0,
                "reblogs_count": 0,
                "favourites_count": 0,
            },
        ]
        mock_client.account_statuses.return_value = mock_statuses

        mastodon_platform._authenticated = True
        mastodon_platform.client = mock_client

        posts = await mastodon_platform.get_posts(
            start_date=datetime(2024, 1, 10), end_date=datetime(2024, 1, 20)
        )

        # Only the post within the date range should be returned
        assert len(posts) == 1
        assert posts[0].id == "status2"

    @pytest.mark.asyncio
    async def test_get_posts_handles_api_exception(
        self, mastodon_platform, mock_mastodon_config
    ):
        """Test that get_posts handles API exceptions gracefully."""
        mock_client = Mock()
        mock_client.me.return_value = {"id": "123456"}
        mock_client.account_statuses.side_effect = Exception("API Error")

        mastodon_platform._authenticated = True
        mastodon_platform.client = mock_client

        posts = await mastodon_platform.get_posts(
            start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 2)
        )

        assert posts == []


class TestMastodonDeletePost:
    """Test cases for Mastodon post deletion."""

    @pytest.mark.asyncio
    async def test_delete_post_success(self, mastodon_platform, mock_mastodon_config):
        """Test successful post deletion."""
        mock_client = Mock()
        mastodon_platform._authenticated = True
        mastodon_platform.client = mock_client

        result = await mastodon_platform.delete_post("status123")

        assert result.success is True
        assert result.post_id == "status123"
        mock_client.status_delete.assert_called_once_with("status123")

    @pytest.mark.asyncio
    async def test_delete_post_failure(self, mastodon_platform, mock_mastodon_config):
        """Test post deletion failure due to API error."""
        mock_client = Mock()
        mock_client.status_delete.side_effect = Exception("API error")
        mastodon_platform._authenticated = True
        mastodon_platform.client = mock_client

        result = await mastodon_platform.delete_post("status123")

        assert result.success is False
        assert "API error" in result.error

    @pytest.mark.asyncio
    async def test_delete_post_not_authenticated(self, mastodon_platform):
        """Test deletion fails when not authenticated."""
        mastodon_platform._authenticated = False
        mastodon_platform.client = None

        result = await mastodon_platform.delete_post("status123")

        assert result.success is False
        assert "Not authenticated" in result.error
