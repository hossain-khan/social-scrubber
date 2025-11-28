"""Test base platform functionality."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from social_scrubber.platforms.base import BasePlatform, DeletionResult, Post


class TestPost:
    """Test Post data class."""

    def test_post_creation(self):
        """Test creating a Post object with required and optional fields."""
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

    def test_post_creation_with_all_fields(self):
        """Test creating a Post object with all fields including optional ones."""
        created_at = datetime.now()
        metadata = {"likes": 10, "retweets": 5}
        post = Post(
            id="456",
            content="Full post",
            created_at=created_at,
            platform="bluesky",
            url="https://example.com/post/456",
            metadata=metadata,
        )

        assert post.id == "456"
        assert post.url == "https://example.com/post/456"
        assert post.metadata == metadata

    def test_post_string_representation(self):
        """Test Post __str__ returns formatted string with platform, date, and content."""
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
        """Test Post __str__ truncates content longer than 50 chars with ellipsis."""
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
        """Test successful deletion result has success=True and no error."""
        result = DeletionResult(post_id="123", success=True)

        assert result.post_id == "123"
        assert result.success is True
        assert result.error is None
        assert result.archived is False
        assert result.archive_path is None

    def test_deletion_result_failure(self):
        """Test failed deletion result has success=False and an error message."""
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


class ConcretePlatform(BasePlatform):
    """Concrete implementation of BasePlatform for testing."""

    def __init__(self, name: str = "test"):
        super().__init__(name)
        self.delete_post_mock = AsyncMock()

    async def authenticate(self) -> bool:
        return True

    async def get_posts(self, start_date, end_date, limit=None):
        return []

    async def delete_post(self, post_id: str) -> DeletionResult:
        return await self.delete_post_mock(post_id)


class TestBasePlatform:
    """Test BasePlatform class methods."""

    def test_platform_initialization(self):
        """Test that BasePlatform initializes with correct name and auth status."""
        platform = ConcretePlatform("myplatform")

        assert platform.name == "myplatform"
        assert platform._authenticated is False

    def test_is_authenticated_property(self):
        """Test is_authenticated property reflects internal state."""
        platform = ConcretePlatform()

        assert platform.is_authenticated is False

        platform._authenticated = True
        assert platform.is_authenticated is True

    def test_display_name_property(self):
        """Test display_name property returns title-cased platform name."""
        platform = ConcretePlatform("bluesky")
        assert platform.display_name == "Bluesky"

        platform2 = ConcretePlatform("twitter")
        assert platform2.display_name == "Twitter"

    @pytest.mark.asyncio
    async def test_archive_post_creates_json_file(self):
        """Test _archive_post creates a JSON file with post data."""
        platform = ConcretePlatform()
        post = Post(
            id="test123",
            content="Test content",
            created_at=datetime(2024, 1, 15, 10, 30),
            platform="test",
            url="https://example.com/post/test123",
            metadata={"key": "value"},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = await platform._archive_post(post, temp_dir)

            assert archive_path is not None
            assert Path(archive_path).exists()

            # Verify the file contents
            with open(archive_path) as f:
                data = json.load(f)

            assert data["platform"] == "test"
            assert data["post_id"] == "test123"
            assert data["content"] == "Test content"
            assert data["url"] == "https://example.com/post/test123"
            assert data["metadata"] == {"key": "value"}
            assert "archived_at" in data

    @pytest.mark.asyncio
    async def test_archive_post_sanitizes_post_id_in_filename(self):
        """Test _archive_post sanitizes special characters in post ID for filename."""
        platform = ConcretePlatform()
        post = Post(
            id="at://did:plc:abc123/app.bsky.feed.post/xyz789",
            content="Test content",
            created_at=datetime(2024, 1, 15, 10, 30),
            platform="test",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = await platform._archive_post(post, temp_dir)

            assert archive_path is not None
            # Check that filename doesn't contain forward slashes or colons
            filename = Path(archive_path).name
            assert "/" not in filename
            assert ":" not in filename

    @pytest.mark.asyncio
    async def test_archive_post_returns_none_on_failure(self):
        """Test _archive_post returns None when archiving fails."""
        platform = ConcretePlatform()
        post = Post(
            id="test123",
            content="Test content",
            created_at=datetime(2024, 1, 15, 10, 30),
            platform="test",
        )

        # Use an invalid path that can't be created
        result = await platform._archive_post(post, "/nonexistent/readonly/path")

        assert result is None

    @pytest.mark.asyncio
    async def test_bulk_delete_posts_deletes_all_posts(self):
        """Test bulk_delete_posts calls delete_post for each post."""
        platform = ConcretePlatform()
        platform.delete_post_mock.return_value = DeletionResult(
            post_id="test", success=True
        )

        posts = [
            Post(
                id="post1",
                content="Content 1",
                created_at=datetime.now(),
                platform="test",
            ),
            Post(
                id="post2",
                content="Content 2",
                created_at=datetime.now(),
                platform="test",
            ),
        ]

        results = await platform.bulk_delete_posts(
            posts, archive_before_delete=False, archive_path="/tmp"
        )

        assert len(results) == 2
        assert platform.delete_post_mock.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_delete_posts_with_archiving(self):
        """Test bulk_delete_posts archives posts before deletion when enabled."""
        platform = ConcretePlatform()
        platform.delete_post_mock.return_value = DeletionResult(
            post_id="test", success=True
        )

        posts = [
            Post(
                id="post1",
                content="Content 1",
                created_at=datetime.now(),
                platform="test",
            ),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            results = await platform.bulk_delete_posts(
                posts, archive_before_delete=True, archive_path=temp_dir
            )

            assert len(results) == 1
            assert results[0].archived is True
            assert results[0].archive_path is not None
            assert Path(results[0].archive_path).exists()

    @pytest.mark.asyncio
    async def test_bulk_delete_posts_without_archiving(self):
        """Test bulk_delete_posts skips archiving when disabled."""
        platform = ConcretePlatform()
        platform.delete_post_mock.return_value = DeletionResult(
            post_id="test", success=True
        )

        posts = [
            Post(
                id="post1",
                content="Content 1",
                created_at=datetime.now(),
                platform="test",
            ),
        ]

        results = await platform.bulk_delete_posts(
            posts, archive_before_delete=False, archive_path="/tmp"
        )

        assert len(results) == 1
        # archived should remain False (not updated) since we didn't archive
        assert results[0].archived is False
        assert results[0].archive_path is None
