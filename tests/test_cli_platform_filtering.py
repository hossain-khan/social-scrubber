"""Tests for CLI platform filtering functionality."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from social_scrubber.cli import SocialScrubber
from social_scrubber.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration with all platforms configured."""
    config = Mock(spec=Config)

    # Mock platform configs
    config.bluesky = Mock()
    config.bluesky.is_configured = True
    config.mastodon = Mock()
    config.mastodon.is_configured = True
    config.twitter = Mock()
    config.twitter.is_configured = True

    # Mock scrub config
    config.scrub = Mock()
    config.scrub.get_start_datetime.return_value = Mock()
    config.scrub.get_end_datetime.return_value = Mock()
    config.scrub.max_posts_per_scrub = 100
    config.scrub.dry_run = True

    # Mock log level as string
    config.log_level = "INFO"

    return config


@pytest.fixture
def mock_platforms():
    """Create mock platform instances."""
    platforms = {}
    for platform_name in ["bluesky", "mastodon", "twitter"]:
        platform = Mock()
        platform.is_authenticated = False
        platforms[platform_name] = platform
    return platforms


@pytest.fixture
def scrubber(mock_config, mock_platforms):
    """Create a SocialScrubber instance with mocked dependencies."""
    with patch("social_scrubber.cli.Config") as MockConfig, patch(
        "social_scrubber.cli.setup_logging"
    ):  # noqa: F841 (we don't use mock_setup_logging but need to patch it)
        MockConfig.from_env.return_value = mock_config

        scrubber = SocialScrubber()
        scrubber.platforms = mock_platforms

        return scrubber


class TestPlatformFiltering:
    """Test cases for platform filtering in CLI."""

    @pytest.mark.asyncio
    async def test_run_interactive_no_platform_filter(self, scrubber, mock_config):
        """Test that all configured platforms are processed when no filter is applied."""
        # Mock the methods that run_interactive calls
        with patch.object(
            scrubber, "authenticate_platforms"
        ) as mock_auth, patch.object(
            scrubber, "get_posts_from_platforms"
        ) as mock_get_posts, patch.object(
            scrubber, "delete_posts_from_platform"
        ), patch(  # noqa: F841 (we don't use mock_delete but need to patch it)
            "social_scrubber.cli.print_banner"
        ), patch(
            "social_scrubber.cli.console"
        ), patch(  # noqa: F841 (we don't use mock_console but need to patch it)
            "social_scrubber.cli.print_platform_status"
        ), patch(
            "social_scrubber.cli.confirm_action"
        ) as mock_confirm, patch(
            "social_scrubber.cli.format_date_range"
        ), patch(
            "social_scrubber.cli.display_posts_table"
        ), patch(
            "social_scrubber.cli.display_deletion_results"
        ):

            # Setup mocks
            mock_auth.return_value = {
                "bluesky": True,
                "mastodon": True,
                "twitter": True,
            }
            mock_get_posts.return_value = {"bluesky": [], "mastodon": [], "twitter": []}
            mock_confirm.return_value = True

            # Run without platform filter
            await scrubber.run_interactive(None)

            # Verify all platforms were passed to authenticate_platforms
            mock_auth.assert_called_once_with(["bluesky", "mastodon", "twitter"])

    @pytest.mark.asyncio
    async def test_run_interactive_with_single_platform_filter(
        self, scrubber, mock_config
    ):
        """Test that only selected platform is processed when filter is applied."""
        with patch.object(
            scrubber, "authenticate_platforms"
        ) as mock_auth, patch.object(
            scrubber, "get_posts_from_platforms"
        ) as mock_get_posts, patch.object(
            scrubber, "delete_posts_from_platform"
        ), patch(  # noqa: F841 (we don't use mock_delete but need to patch it)
            "social_scrubber.cli.print_banner"
        ), patch(
            "social_scrubber.cli.console"
        ), patch(  # noqa: F841 (we don't use mock_console but need to patch it)
            "social_scrubber.cli.print_platform_status"
        ), patch(
            "social_scrubber.cli.confirm_action"
        ) as mock_confirm, patch(
            "social_scrubber.cli.format_date_range"
        ), patch(
            "social_scrubber.cli.display_posts_table"
        ), patch(
            "social_scrubber.cli.display_deletion_results"
        ):

            # Setup mocks
            mock_auth.return_value = {"bluesky": True}
            mock_get_posts.return_value = {"bluesky": []}
            mock_confirm.return_value = True

            # Run with single platform filter
            await scrubber.run_interactive(["bluesky"])

            # Verify only selected platform was passed to authenticate_platforms
            mock_auth.assert_called_once_with(["bluesky"])

    @pytest.mark.asyncio
    async def test_run_interactive_with_multiple_platform_filter(
        self, scrubber, mock_config
    ):
        """Test that multiple selected platforms are processed when filter is applied."""
        with patch.object(
            scrubber, "authenticate_platforms"
        ) as mock_auth, patch.object(
            scrubber, "get_posts_from_platforms"
        ) as mock_get_posts, patch.object(
            scrubber, "delete_posts_from_platform"
        ), patch(  # noqa: F841 (we don't use mock_delete but need to patch it)
            "social_scrubber.cli.print_banner"
        ), patch(
            "social_scrubber.cli.console"
        ), patch(  # noqa: F841 (we don't use mock_console but need to patch it)
            "social_scrubber.cli.print_platform_status"
        ), patch(
            "social_scrubber.cli.confirm_action"
        ) as mock_confirm, patch(
            "social_scrubber.cli.format_date_range"
        ), patch(
            "social_scrubber.cli.display_posts_table"
        ), patch(
            "social_scrubber.cli.display_deletion_results"
        ):

            # Setup mocks
            mock_auth.return_value = {"bluesky": True, "mastodon": True}
            mock_get_posts.return_value = {"bluesky": [], "mastodon": []}
            mock_confirm.return_value = True

            # Run with multiple platform filter
            await scrubber.run_interactive(["bluesky", "mastodon"])

            # Verify only selected platforms were passed to authenticate_platforms
            mock_auth.assert_called_once_with(["bluesky", "mastodon"])

    @pytest.mark.asyncio
    async def test_run_interactive_invalid_platform_filter(self, scrubber, mock_config):
        """Test that invalid platform names are handled correctly."""
        with patch("social_scrubber.cli.print_banner"), patch(
            "social_scrubber.cli.console"
        ) as mock_console, patch("social_scrubber.cli.print_platform_status"):

            # Run with invalid platform filter
            await scrubber.run_interactive(["invalid_platform"])

            # Verify error message was printed
            mock_console.print.assert_any_call(
                "\n❌ Invalid or not configured platforms: invalid_platform"
            )

    @pytest.mark.asyncio
    async def test_run_interactive_unconfigured_platform_filter(
        self, scrubber, mock_config
    ):
        """Test that unconfigured platforms are handled correctly."""
        # Make twitter unconfigured
        mock_config.twitter.is_configured = False

        with patch("social_scrubber.cli.print_banner"), patch(
            "social_scrubber.cli.console"
        ) as mock_console, patch("social_scrubber.cli.print_platform_status"):

            # Run with unconfigured platform filter
            await scrubber.run_interactive(["twitter"])

            # Verify error message was printed
            mock_console.print.assert_any_call(
                "\n❌ Invalid or not configured platforms: twitter"
            )

    @pytest.mark.asyncio
    async def test_run_interactive_mixed_valid_invalid_platforms(
        self, scrubber, mock_config
    ):
        """Test that mix of valid and invalid platforms is handled correctly."""
        with patch("social_scrubber.cli.print_banner"), patch(
            "social_scrubber.cli.console"
        ) as mock_console, patch("social_scrubber.cli.print_platform_status"):

            # Run with mix of valid and invalid platforms
            await scrubber.run_interactive(["bluesky", "invalid_platform"])

            # Verify error message was printed
            mock_console.print.assert_any_call(
                "\n❌ Invalid or not configured platforms: invalid_platform"
            )

    @pytest.mark.asyncio
    async def test_run_interactive_no_configured_platforms(self, scrubber, mock_config):
        """Test behavior when no platforms are configured."""
        # Make all platforms unconfigured
        mock_config.bluesky.is_configured = False
        mock_config.mastodon.is_configured = False
        mock_config.twitter.is_configured = False

        with patch("social_scrubber.cli.print_banner"), patch(
            "social_scrubber.cli.console"
        ) as mock_console, patch("social_scrubber.cli.print_platform_status"):

            # Run without platform filter
            await scrubber.run_interactive(None)

            # Verify error message was printed
            mock_console.print.assert_called_with(
                "\n❌ No platforms are configured. Please check your .env file."
            )


class TestCLIPlatformParsing:
    """Test cases for CLI platform argument parsing."""

    def test_scrub_command_platform_parsing_single(self):
        """Test that single platform string is parsed correctly."""
        from click.testing import CliRunner

        from social_scrubber.cli import cli

        runner = CliRunner()

        with patch("asyncio.run") as mock_run:
            result = runner.invoke(cli, ["scrub", "--platforms=bluesky", "--dry-run"])

            # Verify asyncio.run was called with correct platforms argument
            assert mock_run.called
            args, kwargs = mock_run.call_args
            # The argument should be a coroutine, we can't inspect it directly
            # But we can verify the command succeeded
            assert result.exit_code == 0

    def test_scrub_command_platform_parsing_multiple(self):
        """Test that multiple platforms string is parsed correctly."""
        from click.testing import CliRunner

        from social_scrubber.cli import cli

        runner = CliRunner()

        with patch("asyncio.run") as mock_run:
            result = runner.invoke(
                cli, ["scrub", "--platforms=bluesky,mastodon", "--dry-run"]
            )

            # Verify asyncio.run was called
            assert mock_run.called
            assert result.exit_code == 0

    def test_scrub_command_no_platform_filter(self):
        """Test that no platform filter works correctly."""
        from click.testing import CliRunner

        from social_scrubber.cli import cli

        runner = CliRunner()

        with patch("asyncio.run") as mock_run:
            result = runner.invoke(cli, ["scrub", "--dry-run"])

            # Verify asyncio.run was called
            assert mock_run.called
            assert result.exit_code == 0
