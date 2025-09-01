"""Test base platform functionality."""

from datetime import datetime, timedelta

import pytest

from social_scrubber.platforms.base import DeletionResult, Post


class TestPost:
    """Test Post data class."""

    def test_post_creation(self):
        """Test creating a Post object."""
        created_at = datetime.now()
        post = Post(
            id="123", content="Hello, world!", created_at=created_at, platform="test"
        )

        assert post.id == "123"
        assert post.content == "Hello, world!"
        assert post.created_at == created_at
        assert post.platform == "test"
        assert post.url is None
        assert post.metadata is None

    def test_post_string_representation(self):
        """Test Post string representation."""
        created_at = datetime(2024, 1, 15, 10, 30, 0)
        post = Post(
            id="123",
            content="This is a test post with some content",
            created_at=created_at,
            platform="test",
        )

        str_repr = str(post)
        assert "test" in str_repr.lower()
        assert "2024-01-15 10:30" in str_repr
        assert "This is a test post" in str_repr

    def test_post_long_content_truncation(self):
        """Test Post string representation with long content."""
        created_at = datetime(2024, 1, 15, 10, 30, 0)
        long_content = "A" * 100  # 100 character string

        post = Post(
            id="123", content=long_content, created_at=created_at, platform="test"
        )

        str_repr = str(post)
        # Should be truncated with "..."
        assert "..." in str_repr
        assert len(str_repr.split(": ")[1]) <= 53  # 50 chars + "..."


class TestDeletionResult:
    """Test DeletionResult data class."""

    def test_deletion_result_success(self):
        """Test successful deletion result."""
        result = DeletionResult(post_id="123", success=True)

        assert result.post_id == "123"
        assert result.success is True
        assert result.error is None
        assert result.archived is False
        assert result.archive_path is None

    def test_deletion_result_failure(self):
        """Test failed deletion result."""
        result = DeletionResult(post_id="123", success=False, error="Network error")

        assert result.post_id == "123"
        assert result.success is False
        assert result.error == "Network error"

    def test_deletion_result_with_archive(self):
        """Test deletion result with archive information."""
        result = DeletionResult(
            post_id="123",
            success=True,
            archived=True,
            archive_path="/path/to/archive.json",
        )

        assert result.post_id == "123"
        assert result.success is True
        assert result.archived is True
        assert result.archive_path == "/path/to/archive.json"
