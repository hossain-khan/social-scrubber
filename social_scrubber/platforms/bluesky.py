"""Bluesky platform implementation."""

import asyncio
from datetime import datetime
from typing import List, Optional
from dateutil import parser as date_parser
from atproto import Client, models
from ..config import BlueskyConfig
from .base import BasePlatform, Post, DeletionResult


class BlueskyPlatform(BasePlatform):
    """Bluesky platform implementation."""
    
    def __init__(self, config: BlueskyConfig):
        """Initialize Bluesky platform.
        
        Args:
            config: Bluesky configuration
        """
        super().__init__("bluesky")
        self.config = config
        self.client: Optional[Client] = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Bluesky.
        
        Returns:
            True if authentication successful, False otherwise.
        """
        if not self.config.is_configured:
            print("❌ Bluesky configuration missing. Please check BLUESKY_HANDLE and BLUESKY_PASSWORD.")
            return False
        
        try:
            self.client = Client()
            profile = self.client.login(self.config.handle, self.config.password)
            self._authenticated = True
            print(f"✅ Successfully authenticated with Bluesky as @{profile.handle}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to authenticate with Bluesky: {e}")
            self._authenticated = False
            return False
    
    async def get_posts(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        limit: Optional[int] = None
    ) -> List[Post]:
        """Retrieve posts from Bluesky within the specified date range.
        
        Args:
            start_date: Start date for posts to retrieve
            end_date: End date for posts to retrieve
            limit: Maximum number of posts to retrieve
            
        Returns:
            List of Post objects
        """
        if not self._authenticated or not self.client:
            raise RuntimeError("Not authenticated with Bluesky")
        
        posts = []
        cursor = None
        collected = 0
        
        try:
            while True:
                # Get posts from the API
                response = self.client.app.bsky.feed.get_author_feed(
                    actor=self.config.handle,
                    limit=min(50, limit - collected) if limit else 50,
                    cursor=cursor
                )
                
                if not response.feed:
                    break
                
                for feed_item in response.feed:
                    if not feed_item.post:
                        continue
                    
                    post_record = feed_item.post.record
                    if not hasattr(post_record, 'created_at'):
                        continue
                    
                    # Parse the created date with proper timezone handling
                    try:
                        created_at = date_parser.isoparse(post_record.created_at)
                        # Convert to naive datetime for comparison (assumes UTC)
                        if created_at.tzinfo is not None:
                            created_at = created_at.replace(tzinfo=None)
                    except (ValueError, AttributeError) as e:
                        print(f"Warning: Failed to parse date for post {feed_item.post.uri}: {e}")
                        continue
                    
                    # Filter by date range
                    if created_at < start_date or created_at > end_date:
                        if created_at < start_date:
                            # We've gone too far back, stop fetching
                            return posts
                        continue
                    
                    # Extract post content
                    content = getattr(post_record, 'text', '')
                    
                    # Create Post object
                    post = Post(
                        id=feed_item.post.uri,
                        content=content,
                        created_at=created_at,
                        platform=self.name,
                        url=f"https://bsky.app/profile/{self.config.handle}/post/{feed_item.post.uri.split('/')[-1]}",
                        metadata={
                            'uri': feed_item.post.uri,
                            'cid': feed_item.post.cid,
                            'author': feed_item.post.author.handle if feed_item.post.author else None
                        }
                    )
                    
                    posts.append(post)
                    collected += 1
                    
                    if limit and collected >= limit:
                        return posts
                
                # Check if there are more posts to fetch
                cursor = response.cursor
                if not cursor:
                    break
            
            return posts
            
        except Exception as e:
            print(f"❌ Error retrieving Bluesky posts: {e}")
            return []
    
    async def delete_post(self, post_id: str) -> DeletionResult:
        """Delete a specific Bluesky post.
        
        Args:
            post_id: URI of the post to delete
            
        Returns:
            DeletionResult indicating success/failure and details
        """
        if not self._authenticated or not self.client:
            return DeletionResult(
                post_id=post_id,
                success=False,
                error="Not authenticated with Bluesky"
            )
        
        try:
            # The post_id is the AT Protocol URI
            # We need to extract the record key from it
            uri_parts = post_id.split('/')
            if len(uri_parts) < 2:
                return DeletionResult(
                    post_id=post_id,
                    success=False,
                    error="Invalid post URI format"
                )
            
            rkey = uri_parts[-1]  # The record key is the last part of the URI
            
            # Delete the post
            self.client.app.bsky.feed.post.delete(rkey)
            
            return DeletionResult(
                post_id=post_id,
                success=True
            )
            
        except Exception as e:
            return DeletionResult(
                post_id=post_id,
                success=False,
                error=str(e)
            )
