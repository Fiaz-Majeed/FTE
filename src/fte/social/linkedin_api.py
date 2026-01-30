"""LinkedIn API Integration - Handle LinkedIn API operations for posting and retrieval."""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from linkedin_api import Linkedin
    LINKEDIN_API_AVAILABLE = True
except ImportError:
    LINKEDIN_API_AVAILABLE = False


class LinkedInAPI:
    """LinkedIn API client for posting and retrieving data."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        profile_url: str | None = None,
    ):
        """Initialize LinkedIn API client.

        Args:
            username: LinkedIn username/email
            password: LinkedIn password
            profile_url: LinkedIn profile URL (optional)
        """
        if not LINKEDIN_API_AVAILABLE:
            raise ImportError(
                "linkedin-api is required for LinkedIn operations. "
                "Install with: pip install linkedin-api"
            )

        self.username = username
        self.password = password
        self.profile_url = profile_url
        self.client = None
        self._authenticated = False

    def authenticate(self) -> bool:
        """Authenticate with LinkedIn API.

        Returns:
            True if authentication successful
        """
        if not self.username or not self.auth_token:
            # Try to load from environment or config
            import os
            self.username = self.username or os.getenv("LINKEDIN_USERNAME")
            self.password = self.password or os.getenv("LINKEDIN_PASSWORD")

        if not self.username or not self.password:
            raise ValueError(
                "LinkedIn credentials not provided. Set username/password "
                "or environment variables LINKEDIN_USERNAME/LINKEDIN_PASSWORD"
            )

        try:
            self.client = Linkedin(self.username, self.password)
            self._authenticated = True
            return True
        except Exception as e:
            print(f"LinkedIn authentication failed: {e}")
            return False

    def post_update(
        self,
        text: str,
        visibility: str = "PUBLIC",  # PUBLIC, CONNECTIONS_ONLY
        hashtags: List[str] | None = None,
        images: List[str] | None = None,
    ) -> Dict[str, Any]:
        """Post an update to LinkedIn.

        Args:
            text: Text content of the post
            visibility: Post visibility (PUBLIC or CONNECTIONS_ONLY)
            hashtags: List of hashtags to include
            images: List of image file paths to attach

        Returns:
            Dictionary with post result and ID
        """
        if not self._authenticated:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}

        try:
            # Add hashtags to text if provided
            if hashtags:
                text += " " + " ".join([f"#{tag}" for tag in hashtags])

            # For now, using the basic post method
            # In a real implementation, this would use the actual LinkedIn API method
            result = self.client.post_share(comment=text, visibility=visibility)

            post_result = {
                "success": True,
                "post_id": result.get("id", "unknown") if isinstance(result, dict) else "unknown",
                "text": text,
                "visibility": visibility,
                "timestamp": datetime.now().isoformat(),
                "hashtags": hashtags or [],
            }

            return post_result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_profile_info(self) -> Dict[str, Any]:
        """Get current user profile information.

        Returns:
            Dictionary with profile information
        """
        if not self._authenticated:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}

        try:
            # Get profile info
            profile = self.client.get_profile(self.username.replace("@", "").split()[0])
            return {
                "success": True,
                "profile": profile,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_network_info(self) -> Dict[str, Any]:
        """Get network information (connections count, etc.).

        Returns:
            Dictionary with network information
        """
        if not self._authenticated:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}

        try:
            # Get network info
            connections = self.client.get_connections()
            return {
                "success": True,
                "connection_count": len(connections) if connections else 0,
                "connections": connections,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific post.

        Args:
            post_id: LinkedIn post ID

        Returns:
            Dictionary with post analytics
        """
        if not self._authenticated:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}

        try:
            # Get post analytics
            # Note: Actual LinkedIn API may have different method
            analytics = {}
            return {
                "success": True,
                "post_id": post_id,
                "analytics": analytics,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


def create_post_from_vault_content(
    content: str,
    max_length: int = 280,  # LinkedIn allows up to 3000 characters, but shorter is better
    hashtags: List[str] | None = None,
) -> str:
    """Create a LinkedIn post from vault content.

    Args:
        content: Original content from vault
        max_length: Maximum length of the post
        hashtags: List of hashtags to append

    Returns:
        Formatted post content
    """
    # Clean up the content - remove markdown, keep essential info
    import re

    # Remove markdown headers but keep the text
    content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)

    # Remove other markdown but keep the text
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)      # Italics
    content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)  # Links

    # Truncate to max length
    if len(content) > max_length:
        content = content[:max_length - 3] + "..."

    # Add hashtags if provided
    if hashtags:
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
        # Ensure total length doesn't exceed max_length
        if len(content) + len(hashtag_str) + 1 <= max_length:
            content = f"{content} {hashtag_str}"
        else:
            # Truncate content to fit hashtags
            available_space = max_length - len(hashtag_str) - 1
            if available_space > 0:
                content = content[:available_space] + "..."
                content = f"{content} {hashtag_str}"

    return content


def get_recent_vault_notes(
    vault_path: str | Path | None = None,
    days_back: int = 7,
    tags: List[str] | None = None,
) -> List[Dict[str, Any]]:
    """Get recent notes from vault that might be suitable for LinkedIn posting.

    Args:
        vault_path: Path to vault directory
        days_back: Number of days back to look for notes
        tags: Only include notes with these tags

    Returns:
        List of notes that could be converted to LinkedIn posts
    """
    from ..vault_manager import VaultManager

    base_path = Path(__file__).parent.parent.parent
    if vault_path is None:
        vault_path = base_path / "vault"

    manager = VaultManager(vault_path)

    # Look in Inbox and Needs_Action for recent notes
    notes = []

    # Calculate cutoff date
    cutoff_date = datetime.now()
    cutoff_date = cutoff_date.fromtimestamp(cutoff_date.timestamp() - (days_back * 24 * 3600))

    for folder in ["Inbox", "Needs_Action"]:
        files = manager.list_files(folder)

        for file_path in files:
            # Check if file is recent enough
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)

            if mod_time >= cutoff_date:
                content = file_path.read_text(encoding="utf-8")

                # Check if file has required tags (if specified)
                has_required_tags = True
                if tags:
                    # Look for tags in frontmatter
                    if "---" in content:
                        frontmatter_end = content.find("---", 3)
                        if frontmatter_end != -1:
                            frontmatter = content[3:frontmatter_end]
                            for tag in tags:
                                if f"#{tag}" in frontmatter or tag in frontmatter:
                                    break
                            else:
                                has_required_tags = False

                if has_required_tags:
                    notes.append({
                        "path": str(file_path),
                        "name": file_path.stem,
                        "content": content,
                        "modified": mod_time.isoformat(),
                        "folder": folder,
                    })

    return notes