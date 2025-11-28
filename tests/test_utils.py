"""Test utilities module."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from social_scrubber.platforms.base import DeletionResult, Post
from social_scrubber.utils import (
    confirm_action,
    display_deletion_results,
    display_posts_table,
    ensure_archive_directory,
    format_date_range,
    print_banner,
    print_platform_status,
    setup_logging,
)


class TestSetupLogging:
    """Test setup_logging function."""

    def test_setup_logging_with_default_level(self):
        """Test setup_logging with default INFO level."""
        # Should not raise any exceptions
        setup_logging()

    def test_setup_logging_with_debug_level(self):
        """Test setup_logging with DEBUG level."""
        setup_logging("DEBUG")

    def test_setup_logging_with_warning_level(self):
        """Test setup_logging with WARNING level."""
        setup_logging("WARNING")


class TestFormatDateRange:
    """Test format_date_range function."""

    def test_format_date_range_returns_arrow_separated_dates(self):
        """Test that format_date_range returns dates separated by arrow."""
        start = datetime(2024, 1, 1, 10, 30)
        end = datetime(2024, 1, 31, 23, 59)

        result = format_date_range(start, end)

        assert "2024-01-01 10:30" in result
        assert "2024-01-31 23:59" in result
        assert "→" in result

    def test_format_date_range_with_same_date(self):
        """Test format_date_range when start and end are the same."""
        date = datetime(2024, 6, 15, 12, 0)

        result = format_date_range(date, date)

        assert result.count("2024-06-15 12:00") == 2


class TestEnsureArchiveDirectory:
    """Test ensure_archive_directory function."""

    def test_ensure_archive_directory_creates_new_directory(self):
        """Test that ensure_archive_directory creates a new directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "archives" / "subdir"

            result = ensure_archive_directory(str(new_dir))

            assert result is True
            assert new_dir.exists()

    def test_ensure_archive_directory_existing_directory(self):
        """Test ensure_archive_directory with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = ensure_archive_directory(temp_dir)

            assert result is True

    def test_ensure_archive_directory_failure(self):
        """Test ensure_archive_directory returns False on failure."""
        # Using an invalid path that can't be created
        with patch("social_scrubber.utils.Path.mkdir", side_effect=PermissionError):
            result = ensure_archive_directory("/nonexistent/path")

            assert result is False


class TestConfirmAction:
    """Test confirm_action function."""

    def test_confirm_action_yes_response(self):
        """Test confirm_action with 'y' response."""
        with patch("social_scrubber.utils.console") as mock_console:
            mock_console.input.return_value = "y"

            result = confirm_action("Continue?")

            assert result is True

    def test_confirm_action_yes_full_response(self):
        """Test confirm_action with 'yes' response."""
        with patch("social_scrubber.utils.console") as mock_console:
            mock_console.input.return_value = "yes"

            result = confirm_action("Continue?")

            assert result is True

    def test_confirm_action_no_response(self):
        """Test confirm_action with 'n' response."""
        with patch("social_scrubber.utils.console") as mock_console:
            mock_console.input.return_value = "n"

            result = confirm_action("Continue?")

            assert result is False

    def test_confirm_action_empty_response_default_false(self):
        """Test confirm_action with empty response and default False."""
        with patch("social_scrubber.utils.console") as mock_console:
            mock_console.input.return_value = ""

            result = confirm_action("Continue?", default=False)

            assert result is False

    def test_confirm_action_empty_response_default_true(self):
        """Test confirm_action with empty response and default True."""
        with patch("social_scrubber.utils.console") as mock_console:
            mock_console.input.return_value = ""

            result = confirm_action("Continue?", default=True)

            assert result is True


class TestPrintBanner:
    """Test print_banner function."""

    def test_print_banner_outputs_text(self):
        """Test that print_banner outputs the banner text."""
        with patch("social_scrubber.utils.console") as mock_console:
            print_banner()

            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert "SOCIAL SCRUBBER" in call_args


class TestPrintPlatformStatus:
    """Test print_platform_status function."""

    def test_print_platform_status_authenticated(self):
        """Test print_platform_status for authenticated platform."""
        with patch("social_scrubber.utils.console") as mock_console:
            print_platform_status("bluesky", True, True)

            call_args = mock_console.print.call_args[0][0]
            assert "✅" in call_args
            assert "Bluesky" in call_args
            assert "Ready" in call_args

    def test_print_platform_status_configured_not_authenticated(self):
        """Test print_platform_status for configured but not authenticated platform."""
        with patch("social_scrubber.utils.console") as mock_console:
            print_platform_status("mastodon", True, False)

            call_args = mock_console.print.call_args[0][0]
            assert "⚠️" in call_args
            assert "Mastodon" in call_args
            assert "Configured but not authenticated" in call_args

    def test_print_platform_status_not_configured(self):
        """Test print_platform_status for not configured platform."""
        with patch("social_scrubber.utils.console") as mock_console:
            print_platform_status("twitter", False, False)

            call_args = mock_console.print.call_args[0][0]
            assert "❌" in call_args
            assert "Twitter" in call_args
            assert "Not configured" in call_args


class TestDisplayPostsTable:
    """Test display_posts_table function."""

    def test_display_posts_table_with_posts(self):
        """Test display_posts_table with a list of posts."""
        posts = [
            Post(
                id="post1",
                content="Hello world",
                created_at=datetime(2024, 1, 15, 10, 30),
                platform="bluesky",
            ),
            Post(
                id="post2",
                content="Another post with longer content that should be truncated",
                created_at=datetime(2024, 1, 16, 12, 0),
                platform="mastodon",
            ),
        ]

        with patch("social_scrubber.utils.console") as mock_console:
            display_posts_table(posts, "Test Posts")

            mock_console.print.assert_called_once()

    def test_display_posts_table_empty_list(self):
        """Test display_posts_table with empty list shows message."""
        with patch("social_scrubber.utils.console") as mock_console:
            display_posts_table([], "Empty Posts")

            call_args = mock_console.print.call_args[0][0]
            assert "No posts found" in call_args


class TestDisplayDeletionResults:
    """Test display_deletion_results function."""

    def test_display_deletion_results_with_results(self):
        """Test display_deletion_results with successful and failed results."""
        results = [
            DeletionResult(post_id="post1", success=True, archived=True),
            DeletionResult(post_id="post2", success=True, archived=False),
            DeletionResult(post_id="post3", success=False, error="Network error"),
        ]

        with patch("social_scrubber.utils.console") as mock_console:
            display_deletion_results(results, "bluesky")

            # Should have been called multiple times for summary and failures
            assert mock_console.print.call_count >= 1

    def test_display_deletion_results_empty_list(self):
        """Test display_deletion_results with empty list does nothing."""
        with patch("social_scrubber.utils.console") as mock_console:
            display_deletion_results([], "bluesky")

            mock_console.print.assert_not_called()

    def test_display_deletion_results_all_successful(self):
        """Test display_deletion_results with all successful results."""
        results = [
            DeletionResult(post_id="post1", success=True),
            DeletionResult(post_id="post2", success=True),
        ]

        with patch("social_scrubber.utils.console") as mock_console:
            display_deletion_results(results, "mastodon")

            # Should show the panel but no failed deletions section
            mock_console.print.assert_called()
