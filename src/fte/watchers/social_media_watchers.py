"""
Twitter Watcher - Monitor Twitter mentions and engagement
"""
import time
from datetime import datetime
from typing import Optional, Callable
from pathlib import Path

from .twitter_api import TwitterAPI
from ..vault_manager import VaultManager
from ..audit.audit_logger import get_audit_logger, AuditEventType


class TwitterWatcher:
    """Watch Twitter for mentions and engagement."""

    def __init__(
        self,
        vault_path: Optional[Path] = None,
        callback: Optional[Callable] = None,
        poll_interval: int = 300  # 5 minutes
    ):
        """Initialize Twitter watcher.

        Args:
            vault_path: Path to vault for storing mentions
            callback: Optional callback for new mentions
            poll_interval: Polling interval in seconds
        """
        self.vault_path = vault_path or Path(__file__).parent.parent.parent.parent / "vault"
        self.vault_manager = VaultManager(vault_path)
        self.callback = callback
        self.poll_interval = poll_interval

        self.twitter_api = TwitterAPI()
        self.audit_logger = get_audit_logger()
        self.last_check: Optional[datetime] = None
        self._running = False

    def process_mention(self, mention: dict):
        """Process a Twitter mention.

        Args:
            mention: Mention data
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_twitter_mention_{mention['id']}.md"

        content = f"""---
type: twitter_mention
tweet_id: {mention['id']}
author_id: {mention['author_id']}
created_at: {mention['created_at']}
metrics: {mention.get('metrics', {})}
---

# Twitter Mention

**From**: User {mention['author_id']}
**Date**: {mention['created_at']}
**Tweet ID**: {mention['id']}

## Content

{mention['text']}

## Metrics

- Likes: {mention.get('metrics', {}).get('like_count', 0)}
- Retweets: {mention.get('metrics', {}).get('retweet_count', 0)}
- Replies: {mention.get('metrics', {}).get('reply_count', 0)}

## Actions

- [ ] Review mention
- [ ] Respond if needed
- [ ] Track engagement
"""

        self.vault_manager.create_note(
            filename=filename,
            content=content,
            folder="Inbox"
        )

        self.audit_logger.log_action(
            action="twitter_mention_captured",
            actor="twitter_watcher",
            resource=mention['id'],
            status="success"
        )

        if self.callback:
            self.callback("mention", mention)

    def check_mentions(self):
        """Check for new mentions."""
        try:
            mentions = self.twitter_api.get_mentions(since_hours=24)

            new_mentions = 0
            for mention in mentions:
                # Check if we've already processed this mention
                mention_file = self.vault_path / "Inbox" / f"*twitter_mention_{mention['id']}.md"
                if not list(self.vault_path.glob(str(mention_file))):
                    self.process_mention(mention)
                    new_mentions += 1

            if new_mentions > 0:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Found {new_mentions} new Twitter mentions")

            self.last_check = datetime.now()

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to check Twitter mentions: {e}",
                actor="twitter_watcher",
                resource="mentions"
            )
            print(f"Error checking Twitter mentions: {e}")

    def start(self):
        """Start watching Twitter."""
        self._running = True
        print(f"Twitter watcher started. Checking every {self.poll_interval} seconds...")

        while self._running:
            self.check_mentions()
            time.sleep(self.poll_interval)

    def stop(self):
        """Stop watching."""
        self._running = False
        print("Twitter watcher stopped.")


class FacebookInstagramWatcher:
    """Watch Facebook and Instagram for engagement."""

    def __init__(
        self,
        vault_path: Optional[Path] = None,
        callback: Optional[Callable] = None,
        poll_interval: int = 600  # 10 minutes
    ):
        """Initialize Facebook/Instagram watcher.

        Args:
            vault_path: Path to vault
            callback: Optional callback
            poll_interval: Polling interval in seconds
        """
        self.vault_path = vault_path or Path(__file__).parent.parent.parent.parent / "vault"
        self.vault_manager = VaultManager(vault_path)
        self.callback = callback
        self.poll_interval = poll_interval

        from .facebook_instagram_api import FacebookAPI
        self.facebook_api = FacebookAPI()
        self.audit_logger = get_audit_logger()
        self.last_check: Optional[datetime] = None
        self._running = False

    def generate_daily_summary(self, platform: str):
        """Generate daily engagement summary.

        Args:
            platform: Platform name (facebook or instagram)
        """
        try:
            summary = self.facebook_api.generate_summary(platform, days=1)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{platform}_daily_summary.md"

            content = f"""---
type: social_media_summary
platform: {platform}
period_days: 1
generated_at: {summary['generated_at']}
---

# {platform.title()} Daily Summary

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Generated**: {summary['generated_at']}

## Metrics

"""

            if platform == "facebook":
                content += f"- **Impressions**: {summary.get('impressions', 'N/A')}\n"
                content += f"- **Engagement**: {summary.get('engagement', 'N/A')}\n"
            else:
                content += f"- **Impressions**: {summary.get('impressions', 'N/A')}\n"
                content += f"- **Reach**: {summary.get('reach', 'N/A')}\n"

            content += "\n## Analysis\n\n"
            content += "Review detailed metrics in the data above.\n"

            self.vault_manager.create_note(
                filename=filename,
                content=content,
                folder="Done"
            )

            self.audit_logger.log_action(
                action=f"{platform}_summary_generated",
                actor="social_watcher",
                resource=filename,
                status="success"
            )

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generated {platform} summary")

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to generate {platform} summary: {e}",
                actor="social_watcher",
                resource=platform
            )
            print(f"Error generating {platform} summary: {e}")

    def check_engagement(self):
        """Check engagement on both platforms."""
        try:
            # Generate summaries for both platforms
            self.generate_daily_summary("facebook")
            self.generate_daily_summary("instagram")

            self.last_check = datetime.now()

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to check social media engagement: {e}",
                actor="social_watcher",
                resource="engagement"
            )
            print(f"Error checking social media: {e}")

    def start(self):
        """Start watching social media."""
        self._running = True
        print(f"Facebook/Instagram watcher started. Checking every {self.poll_interval} seconds...")

        while self._running:
            self.check_engagement()
            time.sleep(self.poll_interval)

    def stop(self):
        """Stop watching."""
        self._running = False
        print("Facebook/Instagram watcher stopped.")
