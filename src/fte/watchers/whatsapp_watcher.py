"""WhatsApp Watcher - Monitor WhatsApp messages using Twilio API."""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Callable, Dict, Any

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

from ..vault_manager import VaultManager


class WhatsAppEventHandler:
    """Handle WhatsApp events (new messages)."""

    def __init__(self, callback: Callable[[str, str, Dict[str, Any]], None] | None = None):
        """Initialize the event handler.

        Args:
            callback: Optional callback function(event_type, message_sid, message_data)
        """
        self.callback = callback

    def _log_event(self, event_type: str, message_sid: str, message_data: Dict[str, Any]) -> None:
        """Log a WhatsApp event.

        Args:
            event_type: Type of event (new_message)
            message_sid: Twilio message SID
            message_data: Dictionary with message details (body, from, to, date)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = message_data.get("body", "(No Body)")
        sender = message_data.get("from", "Unknown")

        print(f"[{timestamp}] {event_type.upper()}: {body[:50]}... (from: {sender})")

        if self.callback:
            self.callback(event_type, message_sid, message_data)

    def on_new_message(self, message_sid: str, message_data: Dict[str, Any]) -> None:
        """Handle new message event."""
        self._log_event("new_message", message_sid, message_data)


class WhatsAppWatcher:
    """Watch WhatsApp messages using Twilio API."""

    def __init__(
        self,
        account_sid: str | None = None,
        auth_token: str | None = None,
        vault_path: str | Path | None = None,
        callback: Callable[[str, str, Dict[str, Any]], None] | None = None,
        poll_interval: int = 60,
        phone_numbers: list[str] | None = None,
    ):
        """Initialize the WhatsApp watcher.

        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            vault_path: Path to the vault directory for saving messages
            callback: Optional callback for events
            poll_interval: Seconds between polling (default: 60)
            phone_numbers: List of phone numbers to monitor (None = all)
        """
        if not TWILIO_AVAILABLE:
            raise ImportError(
                "Twilio is required for WhatsApp watcher. Install with: pip install twilio"
            )

        base_path = Path(__file__).parent.parent.parent

        if vault_path is None:
            vault_path = base_path / "vault"

        self.account_sid = account_sid
        self.auth_token = auth_token
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.poll_interval = poll_interval
        self.phone_numbers = phone_numbers or []
        self.event_handler = WhatsAppEventHandler(callback)
        self._running = False
        self._client = None
        self._seen_sids: set[str] = set()

    def _initialize_client(self) -> None:
        """Initialize Twilio client with credentials."""
        if not self.account_sid or not self.auth_token:
            # Try to load from environment or config
            import os
            self.account_sid = self.account_sid or os.getenv("TWILIO_ACCOUNT_SID")
            self.auth_token = self.auth_token or os.getenv("TWILIO_AUTH_TOKEN")

        if not self.account_sid or not self.auth_token:
            raise ValueError(
                "Twilio credentials not provided. Set account_sid/auth_token "
                "or environment variables TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN"
            )

        self._client = Client(self.account_sid, self.auth_token)

    def _get_message_data(self, message) -> Dict[str, Any]:
        """Extract message data from Twilio message object.

        Args:
            message: Twilio Message object

        Returns:
            Dictionary with message details
        """
        return {
            "sid": message.sid,
            "body": message.body or "",
            "from": message.from_,
            "to": message.to,
            "date_sent": str(message.date_sent),
            "status": message.status,
            "direction": message.direction,
            "num_segments": message.num_segments,
            "media_count": message.num_media,
        }

    def _save_message_to_vault(self, message_data: Dict[str, Any]) -> Path:
        """Save message as markdown file in vault Inbox.

        Args:
            message_data: Dictionary with message details

        Returns:
            Path to the saved file
        """
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        # Determine if this is a business inquiry
        is_business_inquiry = self._is_business_inquiry(message_data)
        opportunity_score = self._calculate_business_opportunity_score(message_data) if is_business_inquiry else 0.0

        # Create safe filename from message preview
        body = message_data.get("body", "No Body")
        safe_body = "".join(c if c.isalnum() or c in " -_" else "_" for c in body)
        safe_body = safe_body[:50].strip()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Add business indicator to filename if it's a business inquiry
        business_prefix = "business_" if is_business_inquiry else ""
        filename = f"whatsapp_{business_prefix}{timestamp}_{safe_body}.md"
        filepath = self.inbox_path / filename

        # Format as markdown
        content = f"""---
type: whatsapp_message
from: {message_data.get('from', 'Unknown')}
to: {message_data.get('to', '')}
date_sent: {message_data.get('date_sent', '')}
status: {message_data.get('status', '')}
direction: {message_data.get('direction', '')}
sid: {message_data.get('sid', '')}
is_business_inquiry: {is_business_inquiry}
opportunity_score: {opportunity_score}
---

# WhatsApp Message

**From:** {message_data.get('from', 'Unknown')}
**To:** {message_data.get('to', '')}
**Date:** {message_data.get('date_sent', '')}
**Status:** {message_data.get('status', '')}
**Business Inquiry:** {'Yes' if is_business_inquiry else 'No'}
**Opportunity Score:** {opportunity_score:.2f}

---
**Message:**
{message_data.get('body', message_data.get('body', ''))}

---
**Response Template Suggestions:**
{self._generate_response_templates(message_data)}
"""

        filepath.write_text(content, encoding="utf-8")
        return filepath

    def _is_business_inquiry(self, message_data: Dict[str, Any]) -> bool:
        """Determine if a message is a business inquiry."""
        body = message_data.get("body", "").lower()
        sender = message_data.get("from", "")

        # Check for business-related keywords
        business_keywords = [
            'hello', 'hi', 'hey',  # greetings often start business conversations
            'project', 'work', 'job', 'contract', 'freelance',
            'consult', 'consultant', 'consulting',
            'hire', 'hiring', 'need', 'looking for',
            'price', 'cost', 'quote', 'budget', 'rate', 'rates',
            'service', 'services', 'offer', 'proposal',
            'business', 'company', 'corporate', 'enterprise',
            'meeting', 'call', 'schedule', 'appointment',
            'collaborate', 'partnership', 'team', 'together',
            'urgent', 'asap', 'immediately',
            'website', 'app', 'development', 'design', 'marketing',
            'contact', 'information', 'details'
        ]

        # Count business-related keywords
        keyword_count = sum(1 for keyword in business_keywords if keyword in body)

        # Consider it a business inquiry if it contains at least 2 business keywords
        # or if it contains specific high-value keywords
        high_value_keywords = ['project', 'work', 'job', 'hire', 'price', 'quote', 'urgent']
        has_high_value_keyword = any(keyword in body for keyword in high_value_keywords)

        return keyword_count >= 2 or has_high_value_keyword

    def _calculate_business_opportunity_score(self, message_data: Dict[str, Any]) -> float:
        """Calculate business opportunity score based on message content."""
        score = 0.0
        body = message_data.get("body", "").lower()

        # Keyword scoring
        scoring_keywords = {
            'urgent': 0.3,
            'asap': 0.3,
            'immediately': 0.3,
            'project': 0.2,
            'work': 0.2,
            'job': 0.2,
            'hire': 0.2,
            'price': 0.15,
            'quote': 0.15,
            'budget': 0.15,
            'meeting': 0.1,
            'call': 0.1,
            'today': 0.1,
            'now': 0.1,
            'important': 0.05
        }

        for keyword, value in scoring_keywords.items():
            if keyword in body:
                score += value

        # Length bonus for detailed inquiries
        if len(body.split()) > 20:
            score += 0.1

        # Deduct points for spam indicators
        spam_indicators = ['buy now', 'click here', 'free money', 'make money']
        for indicator in spam_indicators:
            if indicator in body:
                score -= 0.5

        # Cap the score between 0 and 1
        return max(0.0, min(score, 1.0))

    def _generate_response_templates(self, message_data: Dict[str, Any]) -> str:
        """Generate appropriate response templates based on message content."""
        body = message_data.get("body", "").lower()

        templates = []

        if self._is_business_inquiry(message_data):
            # Business-related template
            templates.append("Thank you for reaching out! I'd be happy to discuss your project further. Could you provide more details about your requirements, timeline, and budget?")

            if any(word in body for word in ['price', 'quote', 'cost']):
                templates.append("I'd be glad to provide you with a quote. Could you share more specifics about the scope of work you're looking for?")

            if any(word in body for word in ['urgent', 'asap', 'urgent']):
                templates.append("I understand this is time-sensitive. I can prioritize your request and will follow up with you shortly to discuss next steps.")
        else:
            # General template
            templates.append("Thanks for your message! I'll review your inquiry and get back to you soon.")

        return "\n\n".join([f"**Template {i+1}:** {template}" for i, template in enumerate(templates)])

    def _check_new_messages(self) -> None:
        """Check for new WhatsApp messages and process them."""
        try:
            # Get recent messages
            messages = self._client.messages.list(limit=10)

            for message in messages:
                msg_sid = message.sid

                if msg_sid not in self._seen_sids:
                    self._seen_sids.add(msg_sid)

                    # Filter by phone numbers if specified
                    if self.phone_numbers and message.from_ not in self.phone_numbers:
                        continue

                    # Skip initial population (don't alert for existing messages)
                    if self._running:
                        message_data = self._get_message_data(message)
                        self.event_handler.on_new_message(msg_sid, message_data)

                        # Save to vault
                        saved_path = self._save_message_to_vault(message_data)
                        print(f"  -> Saved to: {saved_path.name}")

        except Exception as error:
            print(f"WhatsApp API error: {error}")

    def start(self) -> None:
        """Start watching WhatsApp messages."""
        print("Initializing WhatsApp watcher...")
        self._initialize_client()

        # Initial population of seen SIDs (don't process existing messages)
        print("Loading existing messages...")
        self._check_new_messages()

        self._running = True
        print(f"Watching WhatsApp messages (polling every {self.poll_interval}s)")
        print("Press Ctrl+C to stop...")

    def stop(self) -> None:
        """Stop watching."""
        if self._running:
            self._running = False
            print("\nWhatsApp watcher stopped.")

    def run(self) -> None:
        """Run the watcher until interrupted."""
        self.start()
        try:
            while self._running:
                time.sleep(self.poll_interval)
                self._check_new_messages()
        except KeyboardInterrupt:
            self.stop()


def watch(
    account_sid: str | None = None,
    auth_token: str | None = None,
    poll_interval: int = 60,
    phone_numbers: list[str] | None = None,
) -> None:
    """Convenience function to start watching WhatsApp.

    Args:
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        poll_interval: Seconds between polling
        phone_numbers: List of phone numbers to monitor
    """
    watcher = WhatsAppWatcher(
        account_sid=account_sid,
        auth_token=auth_token,
        poll_interval=poll_interval,
        phone_numbers=phone_numbers,
    )
    watcher.run()


if __name__ == "__main__":
    watch()