"""Base platform interface for social media platforms."""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Post:
    """Represents a social media post."""
    id: str
    content: str
    created_at: datetime
    platform: str
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        """String representation of the post."""
        date_str = self.created_at.strftime("%Y-%m-%d %H:%M")
        preview = (self.content[:50] + "...") if len(self.content) > 50 else self.content
        return f"[{self.platform}] {date_str}: {preview}"


@dataclass
class DeletionResult:
    """Result of a post deletion operation."""
    post_id: str
    success: bool
    error: Optional[str] = None
    archived: bool = False
    archive_path: Optional[str] = None


class BasePlatform(ABC):
    """Base class for social media platform implementations."""
    
    def __init__(self, name: str):
        """Initialize the platform.
        
        Args:
            name: Name of the platform (e.g., "bluesky", "mastodon", "twitter")
        """
        self.name = name
        self._authenticated = False
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform.
        
        Returns:
            True if authentication was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    async def get_posts(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        limit: Optional[int] = None
    ) -> List[Post]:
        """Retrieve posts from the platform within the specified date range.
        
        Args:
            start_date: Start date for posts to retrieve
            end_date: End date for posts to retrieve
            limit: Maximum number of posts to retrieve
            
        Returns:
            List of Post objects
        """
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> DeletionResult:
        """Delete a specific post.
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            DeletionResult indicating success/failure and details
        """
        pass
    
    async def bulk_delete_posts(
        self, 
        posts: List[Post], 
        archive_before_delete: bool = True,
        archive_path: str = "./archives"
    ) -> List[DeletionResult]:
        """Delete multiple posts.
        
        Args:
            posts: List of posts to delete
            archive_before_delete: Whether to archive posts before deletion
            archive_path: Path to store archived posts
            
        Returns:
            List of DeletionResult objects
        """
        results = []
        
        for post in posts:
            # Archive if requested
            if archive_before_delete:
                archive_file = await self._archive_post(post, archive_path)
            else:
                archive_file = None
            
            # Delete the post
            result = await self.delete_post(post.id)
            
            # Update result with archive info
            if archive_file:
                result.archived = True
                result.archive_path = archive_file
            
            results.append(result)
        
        return results
    
    async def _archive_post(self, post: Post, archive_path: str) -> Optional[str]:
        """Archive a post to local storage.
        
        Args:
            post: Post to archive
            archive_path: Path to store the archive
            
        Returns:
            Path to the archived file, or None if archiving failed
        """
        try:
            # Create archive directory if it doesn't exist
            Path(archive_path).mkdir(parents=True, exist_ok=True)
            
            # Create filename with timestamp and post ID
            timestamp = post.created_at.strftime("%Y%m%d_%H%M%S")
            filename = f"{self.name}_{timestamp}_{post.id}.json"
            filepath = Path(archive_path) / filename
            
            # Create archive data
            archive_data = {
                "platform": self.name,
                "post_id": post.id,
                "content": post.content,
                "created_at": post.created_at.isoformat(),
                "url": post.url,
                "metadata": post.metadata,
                "archived_at": datetime.now().isoformat()
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(archive_data, f, indent=2, ensure_ascii=False)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Warning: Failed to archive post {post.id}: {e}")
            return None
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the platform is authenticated."""
        return self._authenticated
    
    @property
    def display_name(self) -> str:
        """Get the display name of the platform."""
        return self.name.title()
