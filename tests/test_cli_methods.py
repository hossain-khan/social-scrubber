"""Tests for CLI SocialScrubber class methods."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from social_scrubber.cli import SocialScrubber
from social_scrubber.config import Config
from social_scrubber.platforms.base import DeletionResult, Post


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = Mock(spec=Config)

    # Mock platform configs
    config.bluesky = Mock()
    config.bluesky.is_configured = True
    config.mastodon = Mock()
    config.mastodon.is_configured = True
    config.twitter = Mock()
    config.twitter.is_configured = False

    # Mock scrub config
    config.scrub = Mock()
    config.scrub.get_start_datetime.return_value = datetime(2024, 1, 1)
    config.scrub.get_end_datetime.return_value = datetime(2024, 1, 31)
    config.scrub.max_posts_per_scrub = 100
    config.scrub.dry_run = True
    config.scrub.archive_before_delete = True
    config.scrub.archive_path = "./archives"
    config.scrub.start_date = "7_days_ago"
    config.scrub.end_date = "today"

    # Mock log level
    config.log_level = "INFO"

    return config


@pytest.fixture
def mock_platform():
    """Create a mock platform."""
    platform = Mock()
    platform.is_authenticated = False
    platform._authenticated = False
    platform.display_name = "Test"
    return platform


@pytest.fixture
def scrubber(mock_config):
    """Create a SocialScrubber instance with mocked dependencies."""
    with (
        patch("social_scrubber.cli.Config") as MockConfig,
        patch("social_scrubber.cli.setup_logging"),
        patch("social_scrubber.cli.BlueskyPlatform") as MockBluesky,
        patch("social_scrubber.cli.MastodonPlatform") as MockMastodon,
        patch("social_scrubber.cli.TwitterPlatform") as MockTwitter,
    ):
        MockConfig.from_env.return_value = mock_config

        # Create mock platforms
        mock_bluesky = Mock()
        mock_bluesky.is_authenticated = False
        mock_bluesky.display_name = "Bluesky"
        mock_bluesky.authenticate = AsyncMock(return_value=True)

        mock_mastodon = Mock()
        mock_mastodon.is_authenticated = False
        mock_mastodon.display_name = "Mastodon"
        mock_mastodon.authenticate = AsyncMock(return_value=True)

        mock_twitter = Mock()
        mock_twitter.is_authenticated = False
        mock_twitter.display_name = "Twitter"
        mock_twitter.authenticate = AsyncMock(return_value=False)

        MockBluesky.return_value = mock_bluesky
        MockMastodon.return_value = mock_mastodon
        MockTwitter.return_value = mock_twitter

        scrubber = SocialScrubber()
        scrubber.platforms = {
            "bluesky": mock_bluesky,
            "mastodon": mock_mastodon,
            "twitter": mock_twitter,
        }

        return scrubber


class TestSocialScrubberAuthenticatePlatforms:
    """Test cases for authenticate_platforms method."""

    @pytest.mark.asyncio
    async def test_authenticate_all_platforms(self, scrubber, mock_config):
        """Test authenticating with all platforms."""
        with patch("social_scrubber.cli.console"):
            results = await scrubber.authenticate_platforms()

            assert "bluesky" in results
            assert "mastodon" in results
            assert "twitter" in results

    @pytest.mark.asyncio
    async def test_authenticate_selected_platforms(self, scrubber, mock_config):
        """Test authenticating with selected platforms only."""
        with patch("social_scrubber.cli.console"):
            results = await scrubber.authenticate_platforms(["bluesky"])

            assert "bluesky" in results
            scrubber.platforms["bluesky"].authenticate.assert_called_once()
            scrubber.platforms["mastodon"].authenticate.assert_not_called()

    @pytest.mark.asyncio
    async def test_authenticate_skips_unknown_platforms(self, scrubber, mock_config):
        """Test that unknown platform names are skipped."""
        with patch("social_scrubber.cli.console"):
            results = await scrubber.authenticate_platforms(["unknown_platform"])

            assert len(results) == 0


class TestSocialScrubberGetPosts:
    """Test cases for get_posts_from_platforms method."""

    @pytest.mark.asyncio
    async def test_get_posts_from_authenticated_platforms(self, scrubber, mock_config):
        """Test getting posts from authenticated platforms."""
        # Set up authenticated platform with posts
        scrubber.platforms["bluesky"].is_authenticated = True
        mock_posts = [
            Post(
                id="post1",
                content="Test post",
                created_at=datetime(2024, 1, 15),
                platform="bluesky",
            )
        ]
        scrubber.platforms["bluesky"].get_posts = AsyncMock(return_value=mock_posts)

        with patch("social_scrubber.cli.console"):
            results = await scrubber.get_posts_from_platforms(
                platform_names=["bluesky"],
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 31),
            )

            assert "bluesky" in results
            assert len(results["bluesky"]) == 1

    @pytest.mark.asyncio
    async def test_get_posts_skips_unauthenticated_platforms(
        self, scrubber, mock_config
    ):
        """Test that unauthenticated platforms are skipped."""
        scrubber.platforms["bluesky"].is_authenticated = False

        with patch("social_scrubber.cli.console"):
            results = await scrubber.get_posts_from_platforms(
                platform_names=["bluesky"],
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 31),
            )

            assert "bluesky" not in results

    @pytest.mark.asyncio
    async def test_get_posts_handles_exception(self, scrubber, mock_config):
        """Test that exceptions during post retrieval are handled gracefully."""
        scrubber.platforms["bluesky"].is_authenticated = True
        scrubber.platforms["bluesky"].get_posts = AsyncMock(
            side_effect=Exception("API error")
        )

        with patch("social_scrubber.cli.console"):
            results = await scrubber.get_posts_from_platforms(
                platform_names=["bluesky"],
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 31),
            )

            assert results["bluesky"] == []


class TestSocialScrubberDeletePosts:
    """Test cases for delete_posts_from_platform method."""

    @pytest.mark.asyncio
    async def test_delete_posts_dry_run_mode(self, scrubber, mock_config):
        """Test that dry run mode doesn't actually delete posts."""
        posts = [
            Post(
                id="post1",
                content="Test post",
                created_at=datetime(2024, 1, 15),
                platform="bluesky",
            )
        ]

        with patch("social_scrubber.cli.console"):
            results = await scrubber.delete_posts_from_platform(
                platform_name="bluesky", posts=posts, dry_run=True
            )

            # Dry run should return empty list without deleting
            assert results == []

    @pytest.mark.asyncio
    async def test_delete_posts_empty_list(self, scrubber, mock_config):
        """Test that empty post list returns empty results."""
        with patch("social_scrubber.cli.console"):
            results = await scrubber.delete_posts_from_platform(
                platform_name="bluesky", posts=[], dry_run=False
            )

            assert results == []

    @pytest.mark.asyncio
    async def test_delete_posts_actual_deletion(self, scrubber, mock_config):
        """Test actual post deletion when dry_run is False."""
        posts = [
            Post(
                id="post1",
                content="Test post",
                created_at=datetime(2024, 1, 15),
                platform="bluesky",
            )
        ]

        mock_deletion_results = [DeletionResult(post_id="post1", success=True)]
        scrubber.platforms["bluesky"].bulk_delete_posts = AsyncMock(
            return_value=mock_deletion_results
        )

        with (
            patch("social_scrubber.cli.console"),
            patch("social_scrubber.cli.ensure_archive_directory", return_value=True),
        ):
            results = await scrubber.delete_posts_from_platform(
                platform_name="bluesky", posts=posts, dry_run=False
            )

            assert len(results) == 1
            assert results[0].success is True

    @pytest.mark.asyncio
    async def test_delete_posts_archive_directory_failure(self, scrubber, mock_config):
        """Test that deletion aborts if archive directory creation fails."""
        posts = [
            Post(
                id="post1",
                content="Test post",
                created_at=datetime(2024, 1, 15),
                platform="bluesky",
            )
        ]

        with (
            patch("social_scrubber.cli.console"),
            patch("social_scrubber.cli.ensure_archive_directory", return_value=False),
        ):
            results = await scrubber.delete_posts_from_platform(
                platform_name="bluesky", posts=posts, dry_run=False
            )

            assert results == []


class TestSocialScrubberShowConfig:
    """Test cases for show_config method."""

    def test_show_config_displays_table(self, scrubber, mock_config):
        """Test that show_config displays configuration table."""
        with patch("social_scrubber.cli.console") as mock_console:
            scrubber.show_config()

            # Should have called console.print multiple times
            assert mock_console.print.call_count >= 1


class TestSocialScrubberTestConnections:
    """Test cases for test_connections method."""

    @pytest.mark.asyncio
    async def test_test_connections_no_configured_platforms(
        self, scrubber, mock_config
    ):
        """Test test_connections when no platforms are configured."""
        mock_config.bluesky.is_configured = False
        mock_config.mastodon.is_configured = False
        mock_config.twitter.is_configured = False

        with patch("social_scrubber.cli.console") as mock_console:
            await scrubber.test_connections()

            # Should print error message about no configured platforms
            calls = [str(call) for call in mock_console.print.call_args_list]
            assert any("No platforms are configured" in str(call) for call in calls)

    @pytest.mark.asyncio
    async def test_test_connections_successful(self, scrubber, mock_config):
        """Test test_connections with successful authentication."""
        # Make bluesky configured and authentication return True
        mock_config.bluesky.is_configured = True
        scrubber.platforms["bluesky"].authenticate = AsyncMock(return_value=True)

        with patch("social_scrubber.cli.console") as mock_console:
            await scrubber.test_connections()

            # Should print success message
            calls = [str(call) for call in mock_console.print.call_args_list]
            assert any("Connection successful" in str(call) for call in calls)

    @pytest.mark.asyncio
    async def test_test_connections_failed(self, scrubber, mock_config):
        """Test test_connections with failed authentication."""
        # Make bluesky configured but authentication return False
        mock_config.bluesky.is_configured = True
        scrubber.platforms["bluesky"].authenticate = AsyncMock(return_value=False)

        with patch("social_scrubber.cli.console") as mock_console:
            await scrubber.test_connections()

            # Should print failure message
            calls = [str(call) for call in mock_console.print.call_args_list]
            assert any("failed" in str(call).lower() for call in calls)


class TestSocialScrubberArchivePosts:
    """Test cases for archive_posts_from_platform method."""

    @pytest.mark.asyncio
    async def test_archive_posts_empty_list(self, scrubber, mock_config):
        """Test archiving empty post list."""
        results = await scrubber.archive_posts_from_platform(
            platform_name="bluesky", posts=[]
        )

        assert results == []

    @pytest.mark.asyncio
    async def test_archive_posts_success(self, scrubber, mock_config):
        """Test successful post archiving."""
        posts = [
            Post(
                id="post1",
                content="Test post",
                created_at=datetime(2024, 1, 15),
                platform="bluesky",
            )
        ]

        scrubber.platforms["bluesky"]._archive_post = AsyncMock(
            return_value="/archives/post1.json"
        )

        with (
            patch("social_scrubber.cli.ensure_archive_directory", return_value=True),
        ):
            results = await scrubber.archive_posts_from_platform(
                platform_name="bluesky", posts=posts
            )

            assert len(results) == 1
            assert results[0]["archived"] is True
            assert results[0]["archive_path"] == "/archives/post1.json"

    @pytest.mark.asyncio
    async def test_archive_posts_archive_directory_failure(self, scrubber, mock_config):
        """Test archiving fails if directory creation fails."""
        posts = [
            Post(
                id="post1",
                content="Test post",
                created_at=datetime(2024, 1, 15),
                platform="bluesky",
            )
        ]

        with (
            patch("social_scrubber.cli.console"),
            patch("social_scrubber.cli.ensure_archive_directory", return_value=False),
        ):
            results = await scrubber.archive_posts_from_platform(
                platform_name="bluesky", posts=posts
            )

            assert results == []
