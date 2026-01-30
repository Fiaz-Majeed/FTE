"""LinkedIn Post Scheduler - Schedule and manage LinkedIn posts."""

import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from threading import Thread, Event
import schedule
from apscheduler.schedulers.background import BackgroundScheduler

from .linkedin_api import LinkedInAPI, create_post_from_vault_content, get_recent_vault_notes


class LinkedInPostScheduler:
    """Schedule and manage LinkedIn posts."""

    def __init__(
        self,
        linkedin_api: LinkedInAPI,
        vault_path: str | Path | None = None,
    ):
        """Initialize the post scheduler.

        Args:
            linkedin_api: LinkedInAPI instance
            vault_path: Path to vault directory
        """
        self.linkedin_api = linkedin_api
        self.base_path = Path(__file__).parent.parent.parent
        if vault_path is None:
            self.vault_path = self.base_path / "vault"
        else:
            self.vault_path = Path(vault_path)

        self.scheduler = BackgroundScheduler()
        self.scheduled_posts: List[Dict[str, Any]] = []
        self.post_history: List[Dict[str, Any]] = []
        self._running = False

    def start(self) -> None:
        """Start the scheduler."""
        self.scheduler.start()
        self._running = True
        print("LinkedIn post scheduler started.")

    def stop(self) -> None:
        """Stop the scheduler."""
        self.scheduler.shutdown()
        self._running = False
        print("LinkedIn post scheduler stopped.")

    def schedule_post(
        self,
        text: str,
        scheduled_time: datetime,
        visibility: str = "PUBLIC",
        hashtags: List[str] | None = None,
        images: List[str] | None = None,
    ) -> str:
        """Schedule a post for a specific time.

        Args:
            text: Text content of the post
            scheduled_time: When to post
            visibility: Post visibility (PUBLIC or CONNECTIONS_ONLY)
            hashtags: List of hashtags to include
            images: List of image file paths to attach

        Returns:
            Scheduled post ID
        """
        post_id = f"post_{int(time.time())}_{hash(text) % 10000}"

        job = self.scheduler.add_job(
            self._execute_post,
            'date',
            run_date=scheduled_time,
            id=post_id,
            kwargs={
                "text": text,
                "visibility": visibility,
                "hashtags": hashtags,
                "images": images,
                "scheduled_id": post_id,
            }
        )

        scheduled_post = {
            "id": post_id,
            "text": text,
            "scheduled_time": scheduled_time.isoformat(),
            "visibility": visibility,
            "hashtags": hashtags or [],
            "images": images or [],
            "status": "scheduled",
            "job": job,
        }

        self.scheduled_posts.append(scheduled_post)

        # Save to history
        self._save_schedule_state()

        return post_id

    def schedule_recurring_post(
        self,
        text: str,
        interval_hours: int,
        visibility: str = "PUBLIC",
        hashtags: List[str] | None = None,
        images: List[str] | None = None,
    ) -> str:
        """Schedule a recurring post at regular intervals.

        Args:
            text: Text content of the post
            interval_hours: Hours between posts
            visibility: Post visibility
            hashtags: List of hashtags to include
            images: List of image file paths to attach

        Returns:
            Scheduled post ID
        """
        post_id = f"recurring_{int(time.time())}_{hash(text) % 10000}"

        job = self.scheduler.add_job(
            self._execute_post,
            'interval',
            hours=interval_hours,
            id=post_id,
            kwargs={
                "text": text,
                "visibility": visibility,
                "hashtags": hashtags,
                "images": images,
                "scheduled_id": post_id,
            }
        )

        scheduled_post = {
            "id": post_id,
            "text": text,
            "interval_hours": interval_hours,
            "visibility": visibility,
            "hashtags": hashtags or [],
            "images": images or [],
            "status": "recurring",
            "job": job,
        }

        self.scheduled_posts.append(scheduled_post)

        # Save to history
        self._save_schedule_state()

        return post_id

    def _execute_post(
        self,
        text: str,
        visibility: str,
        hashtags: List[str] | None,
        images: List[str] | None,
        scheduled_id: str,
    ) -> Dict[str, Any]:
        """Execute a scheduled post.

        Args:
            text: Text content of the post
            visibility: Post visibility
            hashtags: List of hashtags
            images: List of image paths
            scheduled_id: ID of the scheduled post

        Returns:
            Result of the post operation
        """
        print(f"Executing scheduled post: {scheduled_id}")

        result = self.linkedin_api.post_update(
            text=text,
            visibility=visibility,
            hashtags=hashtags,
            images=images,
        )

        # Update post status
        for post in self.scheduled_posts:
            if post["id"] == scheduled_id:
                post["status"] = "posted" if result["success"] else "failed"
                post["result"] = result
                post["executed_at"] = datetime.now().isoformat()
                break

        # Add to history
        history_entry = {
            "id": scheduled_id,
            "text": text,
            "visibility": visibility,
            "hashtags": hashtags or [],
            "images": images or [],
            "result": result,
            "executed_at": datetime.now().isoformat(),
        }
        self.post_history.append(history_entry)

        # Save state
        self._save_schedule_state()

        return result

    def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post.

        Args:
            post_id: ID of the post to cancel

        Returns:
            True if cancelled successfully
        """
        for i, post in enumerate(self.scheduled_posts):
            if post["id"] == post_id:
                try:
                    self.scheduler.remove_job(post_id)
                    post["status"] = "cancelled"
                    self._save_schedule_state()
                    return True
                except Exception:
                    # Job might have already run
                    post["status"] = "cancelled"
                    self._save_schedule_state()
                    return True

        return False

    def get_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Get list of scheduled posts.

        Returns:
            List of scheduled posts
        """
        return self.scheduled_posts.copy()

    def get_post_history(self) -> List[Dict[str, Any]]:
        """Get post history.

        Returns:
            List of past posts
        """
        return self.post_history.copy()

    def _save_schedule_state(self) -> None:
        """Save current schedule state to file."""
        state_file = self.vault_path / "linkedin_schedule.json"

        state = {
            "scheduled_posts": [
                {k: v for k, v in post.items() if k != 'job'}  # Exclude job objects
                for post in self.scheduled_posts
            ],
            "post_history": self.post_history,
            "last_updated": datetime.now().isoformat(),
        }

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, default=str)

    def _load_schedule_state(self) -> None:
        """Load schedule state from file."""
        state_file = self.vault_path / "linkedin_schedule.json"

        if not state_file.exists():
            return

        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Restore scheduled posts
            self.scheduled_posts = state.get("scheduled_posts", [])
            self.post_history = state.get("post_history", [])

            # Reschedule any remaining scheduled posts
            for post in self.scheduled_posts:
                if post["status"] == "scheduled":
                    # Convert ISO string back to datetime
                    scheduled_time = datetime.fromisoformat(post["scheduled_time"])

                    # Only reschedule if time hasn't passed
                    if scheduled_time > datetime.now():
                        self.scheduler.add_job(
                            self._execute_post,
                            'date',
                            run_date=scheduled_time,
                            id=post["id"],
                            kwargs={
                                "text": post["text"],
                                "visibility": post["visibility"],
                                "hashtags": post.get("hashtags"),
                                "images": post.get("images"),
                                "scheduled_id": post["id"],
                            }
                        )
        except Exception as e:
            print(f"Error loading schedule state: {e}")


def create_business_content_from_vault(
    vault_path: str | Path | None = None,
    content_types: List[str] | None = None,
) -> List[Dict[str, Any]]:
    """Create LinkedIn-appropriate business content from vault notes.

    Args:
        vault_path: Path to vault directory
        content_types: Types of content to include (e.g., ['insights', 'updates', 'announcements'])

    Returns:
        List of content ready for LinkedIn posting
    """
    from ..vault_manager import VaultManager

    base_path = Path(__file__).parent.parent.parent
    if vault_path is None:
        vault_path = base_path / "vault"

    manager = VaultManager(vault_path)

    # Get recent content from vault
    recent_notes = get_recent_vault_notes(vault_path, days_back=7)

    content_list = []

    for note in recent_notes:
        # Determine if this note is suitable for LinkedIn
        content = note["content"]

        # Look for content indicators
        is_suitable = False

        if content_types:
            # Check if note contains specified content types
            for content_type in content_types:
                if content_type.lower() in content.lower():
                    is_suitable = True
                    break
        else:
            # Default: look for business-like content
            business_indicators = [
                "insight", "update", "progress", "achievement", "learning",
                "project", "development", "business", "strategy", "growth"
            ]

            for indicator in business_indicators:
                if indicator in content.lower():
                    is_suitable = True
                    break

        if is_suitable:
            # Create LinkedIn-friendly version
            linkedin_content = create_post_from_vault_content(
                content,
                max_length=280,
                hashtags=["Business", "Growth", "Insights"]  # Default hashtags
            )

            content_list.append({
                "original_note": note["name"],
                "content": linkedin_content,
                "suggested_hashtags": ["Business", "Growth", "Insights"],
                "timestamp": note["modified"],
            })

    return content_list


def suggest_posting_times() -> List[datetime]:
    """Suggest optimal times for LinkedIn posting.

    Returns:
        List of suggested posting times
    """
    now = datetime.now()

    # LinkedIn algorithm typically favors engagement during business hours
    # Common optimal times: Tuesday-Thursday, 8-10 AM or 12-2 PM
    suggested_times = []

    # Next 5 business days
    for i in range(1, 6):
        target_date = now + timedelta(days=i)

        # Skip weekends
        if target_date.weekday() < 5:  # Monday to Friday
            # Morning slot
            morning_time = datetime.combine(target_date.date(), datetime.min.time().replace(hour=9))
            suggested_times.append(morning_time)

            # Lunch slot
            lunch_time = datetime.combine(target_date.date(), datetime.min.time().replace(hour=13))
            suggested_times.append(lunch_time)

    return suggested_times