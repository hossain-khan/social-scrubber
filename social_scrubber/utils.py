"""Utilities for Social Scrubber."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .platforms.base import DeletionResult, Post

console = Console()


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("social_scrubber.log"),
        ],
    )


def display_posts_table(posts: List[Post], title: str = "Posts"):
    """Display posts in a formatted table.

    Args:
        posts: List of posts to display
        title: Title for the table
    """
    if not posts:
        console.print(f"[yellow]No posts found for {title.lower()}[/yellow]")
        return

    table = Table(title=f"{title} ({len(posts)} posts)")
    table.add_column("Platform", style="cyan", no_wrap=True)
    table.add_column("Date", style="magenta", no_wrap=True)
    table.add_column("Content Preview", style="green")
    table.add_column("Post ID", style="dim", no_wrap=True)

    for post in posts:
        content_preview = (
            post.content[:50] + "..." if len(post.content) > 50 else post.content
        )
        # Replace newlines with spaces for table display
        content_preview = content_preview.replace("\n", " ").replace("\r", " ")

        table.add_row(
            post.platform.title(),
            post.created_at.strftime("%Y-%m-%d %H:%M"),
            content_preview,
            post.id[-12:],  # Show last 12 chars of ID
        )

    console.print(table)


def display_deletion_results(results: List[DeletionResult], platform: str):
    """Display deletion results in a formatted way.

    Args:
        results: List of deletion results
        platform: Platform name
    """
    if not results:
        return

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    archived = [r for r in results if r.archived]

    # Summary panel
    summary_text = f"""
✅ Successfully deleted: {len(successful)}
❌ Failed to delete: {len(failed)}
📁 Archived: {len(archived)}
    """

    console.print(
        Panel(
            summary_text.strip(),
            title=f"{platform.title()} Deletion Summary",
            border_style="blue",
        )
    )

    # Show failed deletions if any
    if failed:
        console.print("\n[red]Failed Deletions:[/red]")
        for result in failed:
            console.print(f"  • Post {result.post_id[-12:]}: {result.error}")


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation.

    Args:
        message: Message to display
        default: Default answer if user just presses Enter

    Returns:
        True if user confirms, False otherwise
    """
    suffix = " [Y/n]" if default else " [y/N]"
    response = console.input(f"{message}{suffix}: ").strip().lower()

    if not response:
        return default

    return response in ("y", "yes", "true", "1")


def print_banner():
    """Print the application banner."""
    banner = """
    ╔═══════════════════════════════════════════════╗
    ║              SOCIAL SCRUBBER                  ║
    ║        Bulk delete your social media posts    ║
    ╚═══════════════════════════════════════════════╝
    """
    console.print(banner, style="bold blue")


def print_platform_status(
    platform_name: str, is_configured: bool, is_authenticated: bool
):
    """Print the status of a platform.

    Args:
        platform_name: Name of the platform
        is_configured: Whether the platform is configured
        is_authenticated: Whether the platform is authenticated
    """
    status_icon = "✅" if is_authenticated else ("⚠️" if is_configured else "❌")
    status_text = (
        "Ready"
        if is_authenticated
        else ("Configured but not authenticated" if is_configured else "Not configured")
    )

    console.print(f"{status_icon} {platform_name.title()}: {status_text}")


def format_date_range(start_date: datetime, end_date: datetime) -> str:
    """Format a date range for display.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Formatted date range string
    """
    start_str = start_date.strftime("%Y-%m-%d %H:%M")
    end_str = end_date.strftime("%Y-%m-%d %H:%M")
    return f"{start_str} → {end_str}"


def ensure_archive_directory(archive_path: str) -> bool:
    """Ensure archive directory exists.

    Args:
        archive_path: Path to archive directory

    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(archive_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        console.print(
            f"[red]Failed to create archive directory {archive_path}: {e}[/red]"
        )
        return False
