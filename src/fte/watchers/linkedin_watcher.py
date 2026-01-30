"""LinkedIn Watcher - Monitor LinkedIn notifications and messages."""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Callable, Dict, Any

try:
    from linkedin_api import Linkedin
    LINKEDIN_API_AVAILABLE = True
except ImportError:
    LINKEDIN_API_AVAILABLE = False

from ..vault_manager import VaultManager


class LinkedInEventHandler:
    """Handle LinkedIn events (notifications, messages)."""

    def __init__(self, callback: Callable[[str, str, Dict[str, Any]], None] | None = None):
        """Initialize the event handler.

        Args:
            callback: Optional callback function(event_type, activity_id, activity_data)
        """
        self.callback = callback

    def _log_event(self, event_type: str, activity_id: str, activity_data: Dict[str, Any]) -> None:
        """Log a LinkedIn event.

        Args:
            event_type: Type of event (new_notification, new_message)
            activity_id: LinkedIn activity ID
            activity_data: Dictionary with activity details
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = activity_data.get("title", activity_data.get("summary", "(No Title)"))

        print(f"[{timestamp}] {event_type.upper()}: {title[:50]}...")

        if self.callback:
            self.callback(event_type, activity_id, activity_data)

    def on_new_notification(self, notification_id: str, notification_data: Dict[str, Any]) -> None:
        """Handle new notification event."""
        self._log_event("new_notification", notification_id, notification_data)

    def on_new_message(self, message_id: str, message_data: Dict[str, Any]) -> None:
        """Handle new message event."""
        self._log_event("new_message", message_id, message_data)


class LinkedInWatcher:
    """Watch LinkedIn notifications and messages."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        vault_path: str | Path | None = None,
        callback: Callable[[str, str, Dict[str, Any]], None] | None = None,
        poll_interval: int = 300,  # LinkedIn has stricter rate limits
    ):
        """Initialize the LinkedIn watcher.

        Args:
            username: LinkedIn username/email
            password: LinkedIn password
            vault_path: Path to the vault directory for saving activities
            callback: Optional callback for events
            poll_interval: Seconds between polling (default: 300 for rate limiting)
        """
        if not LINKEDIN_API_AVAILABLE:
            raise ImportError(
                "linkedin-api is required for LinkedIn watcher. "
                "Install with: pip install linkedin-api"
            )

        base_path = Path(__file__).parent.parent.parent

        if vault_path is None:
            vault_path = base_path / "vault"

        self.username = username
        self.password = password
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.poll_interval = poll_interval
        self.event_handler = LinkedInEventHandler(callback)
        self._running = False
        self._linkedin_client = None
        self._seen_activity_ids: set[str] = set()

    def _initialize_client(self) -> None:
        """Initialize LinkedIn client with credentials."""
        if not self.username or not self.password:
            # Try to load from environment or config
            import os
            self.username = self.username or os.getenv("LINKEDIN_USERNAME")
            self.password = self.password or os.getenv("LINKEDIN_PASSWORD")

        if not self.username or not self.password:
            raise ValueError(
                "LinkedIn credentials not provided. Set username/password "
                "or environment variables LINKEDIN_USERNAME/LINKEDIN_PASSWORD"
            )

        self._linkedin_client = Linkedin(self.username, self.password)

    def _get_notifications(self) -> list[Dict[str, Any]]:
        """Get recent LinkedIn notifications.

        Returns:
            List of notification dictionaries
        """
        try:
            # Get recent notifications
            # Using the linkedin-api library to fetch notifications
            if self._linkedin_client:
                # Get network updates (which include connection requests, mentions, etc.)
                network_updates = self._linkedin_client.get_network_updates()

                # Get actual notifications
                notifications = self._linkedin_client.get_notifications()

                # Combine both types of activities
                combined_activities = []

                # Process network updates for connection requests and business opportunities
                for update in network_updates.get('elements', []):
                    activity = self._parse_network_update(update)
                    if activity:
                        combined_activities.append(activity)

                # Process notifications
                for notification in notifications.get('elements', []):
                    activity = self._parse_notification(notification)
                    if activity:
                        combined_activities.append(activity)

                return combined_activities
            else:
                return []
        except Exception as e:
            print(f"Error fetching LinkedIn notifications: {e}")
            return []

    def _parse_network_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """Parse network update into standardized format."""
        try:
            update_entity = update.get('entity', {})

            parsed = {
                'id': update.get('urn', update.get('id', 'unknown')),
                'type': 'network_update',
                'subtype': update.get('updateMetadata', {}).get('category', 'general'),
                'timestamp': update.get('createdTime', datetime.now().isoformat()),
                'title': update.get('updateMetadata', {}).get('summary', 'Network Update'),
                'body': update.get('commentary', {}).get('text', ''),
                'sender': update.get('actor', {}).get('name', {}).get('firstName', '') + ' ' +
                         update.get('actor', {}).get('name', {}).get('lastName', ''),
                'sender_profile_url': update.get('actor', {}).get('publicIdentifier', ''),
                'update_type': update.get('updateType', 'unknown'),
                'raw_data': json.dumps(update, indent=2)
            }

            # Check if this is a business opportunity (connection request, mention, etc.)
            if self._is_business_opportunity(parsed):
                parsed['is_business_opportunity'] = True
                parsed['opportunity_score'] = self._calculate_opportunity_score(parsed)

            return parsed
        except Exception as e:
            print(f"Error parsing network update: {e}")
            return {}

    def _parse_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Parse notification into standardized format."""
        try:
            parsed = {
                'id': notification.get('entityUrn', notification.get('id', 'unknown')),
                'type': 'notification',
                'subtype': notification.get('type', 'general'),
                'timestamp': notification.get('createdAt', datetime.now().isoformat()),
                'title': notification.get('title', {}).get('text', 'Notification'),
                'body': notification.get('message', {}).get('text', ''),
                'sender': notification.get('actor', {}).get('name', {}).get('firstName', '') + ' ' +
                         notification.get('actor', {}).get('name', {}).get('lastName', ''),
                'sender_profile_url': notification.get('actor', {}).get('publicIdentifier', ''),
                'notification_type': notification.get('type', 'unknown'),
                'raw_data': json.dumps(notification, indent=2)
            }

            # Check if this is a business opportunity
            if self._is_business_opportunity(parsed):
                parsed['is_business_opportunity'] = True
                parsed['opportunity_score'] = self._calculate_opportunity_score(parsed)

            return parsed
        except Exception as e:
            print(f"Error parsing notification: {e}")
            return {}

    def _is_business_opportunity(self, activity: Dict[str, Any]) -> bool:
        """Determine if an activity represents a business opportunity."""
        # Check for connection requests
        if 'connection' in activity.get('subtype', '').lower():
            return True

        # Check for mentions in posts
        if 'mention' in activity.get('subtype', '').lower():
            return True

        # Check for messages from potential clients
        title_lower = activity.get('title', '').lower()
        body_lower = activity.get('body', '').lower()

        business_keywords = [
            'collaborate', 'partnership', 'business', 'project', 'consulting',
            'hire', 'work', 'opportunity', 'service', 'proposal', 'offer',
            'meeting', 'call', 'introduction', 'connect'
        ]

        for keyword in business_keywords:
            if keyword in title_lower or keyword in body_lower:
                return True

        return False

    def _calculate_opportunity_score(self, activity: Dict[str, Any]) -> float:
        """Calculate business opportunity score based on various factors."""
        score = 0.0

        # Check if sender has a complete profile
        if activity.get('sender_profile_url'):
            score += 0.2

        # Check for business-related keywords
        title_lower = activity.get('title', '').lower()
        body_lower = activity.get('body', '').lower()

        business_keywords = [
            'collaborate', 'partnership', 'business', 'project', 'consulting',
            'hire', 'work', 'opportunity', 'service', 'proposal', 'offer'
        ]

        for keyword in business_keywords:
            if keyword in title_lower or keyword in body_lower:
                score += 0.3

        # Increase score for connection requests
        if 'connection' in activity.get('subtype', '').lower():
            score += 0.3

        # Cap the score at 1.0
        return min(score, 1.0)

    def _get_messages(self) -> list[Dict[str, Any]]:
        """Get recent LinkedIn messages.

        Returns:
            List of message dictionaries
        """
        try:
            # Get recent messages/conversations
            # Note: The actual LinkedIn API may have different methods
            # This is a placeholder implementation
            messages = []

            # In a real implementation, this would fetch actual messages
            # For now, returning empty list as placeholder
            return messages
        except Exception as e:
            print(f"Error fetching LinkedIn messages: {e}")
            return []

    def _normalize_activity_data(self, raw_data: dict, activity_type: str) -> Dict[str, Any]:
        """Normalize different types of LinkedIn activity data.

        Args:
            raw_data: Raw data from LinkedIn API
            activity_type: Type of activity ('notification' or 'message')

        Returns:
            Normalized activity data
        """
        normalized = {
            "id": raw_data.get("entityUrn", raw_data.get("id", "unknown")),
            "type": activity_type,
            "timestamp": datetime.now().isoformat(),
            "title": raw_data.get("title", raw_data.get("summary", "")),
            "body": raw_data.get("body", raw_data.get("message", "")),
            "sender": raw_data.get("sender", raw_data.get("from", "Unknown")),
            "recipient": raw_data.get("recipient", raw_data.get("to", "Me")),
            "raw_data": json.dumps(raw_data, indent=2),
        }
        return normalized

    def _save_activity_to_vault(self, activity_data: Dict[str, Any]) -> Path:
        """Save LinkedIn activity as markdown file in vault Inbox.

        Args:
            activity_data: Dictionary with activity details

        Returns:
            Path to the saved file
        """
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        # Create safe filename from activity title
        title = activity_data.get("title", "No Title")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        safe_title = safe_title[:50].strip()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        activity_type = activity_data.get("type", "activity")
        filename = f"linkedin_{activity_type}_{timestamp}_{safe_title}.md"
        filepath = self.inbox_path / filename

        # Format as markdown
        content = f"""---
type: linkedin_{activity_data.get('type', 'activity')}
title: {activity_data.get('title', '')}
sender: {activity_data.get('sender', 'Unknown')}
recipient: {activity_data.get('recipient', 'Me')}
timestamp: {activity_data.get('timestamp', '')}
activity_id: {activity_data.get('id', '')}
---

# LinkedIn {activity_data.get('type', 'Activity').title()}

**Title:** {activity_data.get('title', '')}
**From:** {activity_data.get('sender', 'Unknown')}
**To:** {activity_data.get('recipient', 'Me')}
**Time:** {activity_data.get('timestamp', '')}

---
**Content:**
{activity_data.get('body', activity_data.get('body', ''))}

**Raw Data:**
```json
{activity_data.get('raw_data', '{}')}
```
"""

        filepath.write_text(content, encoding="utf-8")
        return filepath

    def _check_new_activities(self) -> None:
        """Check for new LinkedIn activities and process them."""
        try:
            # Get notifications
            notifications = self._get_notifications()
            for notification in notifications:
                activity_id = notification.get("entityUrn", notification.get("id", "unknown"))

                if activity_id not in self._seen_activity_ids:
                    self._seen_activity_ids.add(activity_id)

                    # Skip initial population (don't alert for existing activities)
                    if self._running:
                        normalized_data = self._normalize_activity_data(notification, "notification")
                        self.event_handler.on_new_notification(activity_id, normalized_data)

                        # Save to vault
                        saved_path = self._save_activity_to_vault(normalized_data)
                        print(f"  -> Saved notification to: {saved_path.name}")

            # Get messages
            messages = self._get_messages()
            for message in messages:
                message_id = message.get("id", "unknown")

                if message_id not in self._seen_activity_ids:
                    self._seen_activity_ids.add(message_id)

                    # Skip initial population (don't alert for existing messages)
                    if self._running:
                        normalized_data = self._normalize_activity_data(message, "message")
                        self.event_handler.on_new_message(message_id, normalized_data)

                        # Save to vault
                        saved_path = self._save_activity_to_vault(normalized_data)
                        print(f"  -> Saved message to: {saved_path.name}")

        except Exception as error:
            print(f"LinkedIn API error: {error}")
            # Implement retry logic or backoff here in production

    def start(self) -> None:
        """Start watching LinkedIn activities."""
        print("Initializing LinkedIn watcher...")
        self._initialize_client()

        # Initial population of seen IDs (don't process existing activities)
        print("Loading existing activities...")
        self._check_new_activities()

        self._running = True
        print(f"Watching LinkedIn activities (polling every {self.poll_interval}s)")
        print("Press Ctrl+C to stop...")

    def stop(self) -> None:
        """Stop watching."""
        if self._running:
            self._running = False
            print("\nLinkedIn watcher stopped.")

    def run(self) -> None:
        """Run the watcher until interrupted."""
        self.start()
        try:
            while self._running:
                time.sleep(self.poll_interval)
                self._check_new_activities()
        except KeyboardInterrupt:
            self.stop()


def watch(
    username: str | None = None,
    password: str | None = None,
    poll_interval: int = 300,
) -> None:
    """Convenience function to start watching LinkedIn.

    Args:
        username: LinkedIn username/email
        password: LinkedIn password
        poll_interval: Seconds between polling
    """
    watcher = LinkedInWatcher(
        username=username,
        password=password,
        poll_interval=poll_interval,
    )
    watcher.run()


if __name__ == "__main__":
    watch()