"""LinkedIn Posting Skill - Automate LinkedIn posts about business."""

from pathlib import Path
from typing import Dict, Any, List
from ..social.linkedin_api import LinkedInAPI, create_post_from_vault_content, get_recent_vault_notes
from ..social.post_scheduler import LinkedInPostScheduler, create_business_content_from_vault, suggest_posting_times


def create_linkedin_post(
    content: str,
    username: str | None = None,
    password: str | None = None,
    visibility: str = "PUBLIC",
    hashtags: List[str] | None = None,
) -> Dict[str, Any]:
    """Create and post content to LinkedIn.

    Args:
        content: Content to post
        username: LinkedIn username (optional, uses env var if not provided)
        password: LinkedIn password (optional, uses env var if not provided)
        visibility: Post visibility ('PUBLIC' or 'CONNECTIONS_ONLY')
        hashtags: List of hashtags to include

    Returns:
        Dictionary with post result
    """
    try:
        api = LinkedInAPI(username=username, password=password)

        if not api.authenticate():
            return {
                "success": False,
                "error": "Authentication failed",
                "message": "Could not authenticate with LinkedIn"
            }

        result = api.post_update(
            text=content,
            visibility=visibility,
            hashtags=hashtags
        )

        return {
            "success": result["success"],
            "post_result": result,
            "message": "LinkedIn post created successfully" if result["success"] else "Failed to create post"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error creating LinkedIn post"
        }


def schedule_linkedin_post(
    content: str,
    scheduled_time: str,  # ISO format datetime string
    username: str | None = None,
    password: str | None = None,
    visibility: str = "PUBLIC",
    hashtags: List[str] | None = None,
) -> Dict[str, Any]:
    """Schedule a LinkedIn post for a specific time.

    Args:
        content: Content to post
        scheduled_time: When to post (ISO format datetime string)
        username: LinkedIn username
        password: LinkedIn password
        visibility: Post visibility
        hashtags: List of hashtags to include

    Returns:
        Dictionary with scheduling result
    """
    try:
        api = LinkedInAPI(username=username, password=password)

        if not api.authenticate():
            return {
                "success": False,
                "error": "Authentication failed",
                "message": "Could not authenticate with LinkedIn"
            }

        from datetime import datetime
        scheduled_datetime = datetime.fromisoformat(scheduled_time)

        scheduler = LinkedInPostScheduler(linkedin_api=api)

        post_id = scheduler.schedule_post(
            text=content,
            scheduled_time=scheduled_datetime,
            visibility=visibility,
            hashtags=hashtags
        )

        return {
            "success": True,
            "post_id": post_id,
            "scheduled_time": scheduled_time,
            "message": f"LinkedIn post scheduled: {post_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error scheduling LinkedIn post"
        }


def create_post_from_vault_content(
    vault_path: str | Path | None = None,
    content_type: str = "business_update",
    hashtags: List[str] | None = None,
) -> Dict[str, Any]:
    """Create LinkedIn post content from vault notes.

    Args:
        vault_path: Path to vault directory
        content_type: Type of content to generate
        hashtags: List of hashtags to suggest

    Returns:
        Dictionary with generated content
    """
    try:
        # Get recent business-appropriate content from vault
        business_content_list = create_business_content_from_vault(
            vault_path=vault_path,
            content_types=[content_type] if content_type else None
        )

        if not business_content_list:
            return {
                "success": False,
                "error": "No suitable content found in vault",
                "message": "No recent notes suitable for LinkedIn posting"
            }

        # Use the most recent content
        content_item = business_content_list[0]

        # Use default hashtags if none provided
        if hashtags is None:
            hashtags = content_item.get("suggested_hashtags", ["Business", "Growth", "Insights"])

        return {
            "success": True,
            "content": content_item["content"],
            "source_note": content_item["original_note"],
            "hashtags": hashtags,
            "message": f"Generated post content from: {content_item['original_note']}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error generating post content from vault"
        }


def get_suggested_posting_times(
    count: int = 5,
) -> Dict[str, Any]:
    """Get suggested optimal times for LinkedIn posting.

    Args:
        count: Number of suggested times to return

    Returns:
        Dictionary with suggested posting times
    """
    try:
        suggested_times = suggest_posting_times()

        # Return the first 'count' suggestions
        times_to_return = suggested_times[:count]

        return {
            "success": True,
            "suggested_times": [time.isoformat() for time in times_to_return],
            "message": f"Suggested {len(times_to_return)} optimal posting times"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error getting suggested posting times"
        }


def get_linkedin_profile_info(
    username: str | None = None,
    password: str | None = None,
) -> Dict[str, Any]:
    """Get LinkedIn profile information.

    Args:
        username: LinkedIn username
        password: LinkedIn password

    Returns:
        Dictionary with profile information
    """
    try:
        api = LinkedInAPI(username=username, password=password)

        if not api.authenticate():
            return {
                "success": False,
                "error": "Authentication failed",
                "message": "Could not authenticate with LinkedIn"
            }

        profile_info = api.get_profile_info()

        return {
            "success": profile_info["success"],
            "profile_info": profile_info,
            "message": "Retrieved LinkedIn profile info" if profile_info["success"] else "Failed to retrieve profile info"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error retrieving LinkedIn profile info"
        }


def get_linkedin_network_info(
    username: str | None = None,
    password: str | None = None,
) -> Dict[str, Any]:
    """Get LinkedIn network information.

    Args:
        username: LinkedIn username
        password: LinkedIn password

    Returns:
        Dictionary with network information
    """
    try:
        api = LinkedInAPI(username=username, password=password)

        if not api.authenticate():
            return {
                "success": False,
                "error": "Authentication failed",
                "message": "Could not authenticate with LinkedIn"
            }

        network_info = api.get_network_info()

        return {
            "success": network_info["success"],
            "network_info": network_info,
            "message": "Retrieved LinkedIn network info" if network_info["success"] else "Failed to retrieve network info"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error retrieving LinkedIn network info"
        }