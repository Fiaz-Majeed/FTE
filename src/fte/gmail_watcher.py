"""Gmail Watcher - Monitor Gmail inbox for new emails."""

import time
import base64
import pickle
from pathlib import Path
from datetime import datetime
from typing import Callable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

try:
    from plyer import notification
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False


# Gmail API scope - read-only access
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailEventHandler:
    """Handle Gmail events (new emails)."""

    def __init__(self, callback: Callable[[str, str, dict], None] | None = None):
        """Initialize the event handler.

        Args:
            callback: Optional callback function(event_type, message_id, email_data)
        """
        self.callback = callback

    def _send_notification(self, subject: str, sender: str, snippet: str) -> None:
        """Send desktop notification for new email.

        Args:
            subject: Email subject
            sender: Email sender
            snippet: Email preview snippet
        """
        if not NOTIFICATIONS_ENABLED:
            return

        try:
            # Truncate snippet for notification
            preview = snippet[:100] + "..." if len(snippet) > 100 else snippet

            notification.notify(
                title=f"New Email: {subject[:50]}",
                message=f"From: {sender}\n{preview}",
                app_name="FTE Gmail Watcher",
                timeout=10,
            )
        except Exception as e:
            print(f"Notification error: {e}")

    def _log_event(self, event_type: str, message_id: str, email_data: dict) -> None:
        """Log a Gmail event.

        Args:
            event_type: Type of event (new_email)
            message_id: Gmail message ID
            email_data: Dictionary with email details (subject, from, date, body)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = email_data.get("subject", "(No Subject)")
        sender = email_data.get("from", "Unknown")

        print(f"[{timestamp}] {event_type.upper()}: {subject} (from: {sender})")

        # Send desktop notification
        self._send_notification(subject, sender, email_data.get("snippet", ""))

        if self.callback:
            self.callback(event_type, message_id, email_data)

    def on_new_email(self, message_id: str, email_data: dict) -> None:
        """Handle new email event."""
        self._log_event("new_email", message_id, email_data)


class GmailWatcher:
    """Watch Gmail inbox for new emails."""

    def __init__(
        self,
        credentials_path: str | Path | None = None,
        token_path: str | Path | None = None,
        vault_path: str | Path | None = None,
        callback: Callable[[str, str, dict], None] | None = None,
        poll_interval: int = 60,
    ):
        """Initialize the Gmail watcher.

        Args:
            credentials_path: Path to OAuth credentials.json file
            token_path: Path to store/load token.pickle
            vault_path: Path to the vault directory for saving emails
            callback: Optional callback for events
            poll_interval: Seconds between polling (default: 60)
        """
        base_path = Path(__file__).parent.parent.parent

        if credentials_path is None:
            credentials_path = base_path / "credentials.json"
        if token_path is None:
            token_path = base_path / "token.pickle"
        if vault_path is None:
            vault_path = base_path / "vault"

        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.poll_interval = poll_interval
        self.event_handler = GmailEventHandler(callback)
        self._running = False
        self._service = None
        self._seen_ids: set[str] = set()

    def _authenticate(self) -> Credentials:
        """Authenticate with Gmail API.

        Returns:
            Valid credentials for Gmail API
        """
        creds = None

        # Load existing token
        if self.token_path.exists():
            with open(self.token_path, "rb") as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Download it from Google Cloud Console:\n"
                        "1. Go to https://console.cloud.google.com/apis/credentials\n"
                        "2. Create OAuth 2.0 Client ID (Desktop app)\n"
                        "3. Download and save as 'credentials.json'"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, "wb") as token:
                pickle.dump(creds, token)

        return creds

    def _get_email_data(self, message_id: str) -> dict:
        """Fetch full email data for a message ID.

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with email details
        """
        msg = self._service.users().messages().get(
            userId="me", id=message_id, format="full"
        ).execute()

        headers = msg.get("payload", {}).get("headers", [])
        header_dict = {h["name"].lower(): h["value"] for h in headers}

        # Extract body
        body = ""
        payload = msg.get("payload", {})

        if "body" in payload and payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        elif "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode("utf-8")
                        break

        return {
            "id": message_id,
            "subject": header_dict.get("subject", "(No Subject)"),
            "from": header_dict.get("from", "Unknown"),
            "to": header_dict.get("to", ""),
            "date": header_dict.get("date", ""),
            "body": body,
            "snippet": msg.get("snippet", ""),
        }

    def _save_email_to_vault(self, email_data: dict) -> Path:
        """Save email as markdown file in vault Inbox.

        Args:
            email_data: Dictionary with email details

        Returns:
            Path to the saved file
        """
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        # Create safe filename from subject
        subject = email_data.get("subject", "No Subject")
        safe_subject = "".join(c if c.isalnum() or c in " -_" else "_" for c in subject)
        safe_subject = safe_subject[:50].strip()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{safe_subject}.md"
        filepath = self.inbox_path / filename

        # Format as markdown
        content = f"""---
type: email
from: {email_data.get('from', 'Unknown')}
to: {email_data.get('to', '')}
date: {email_data.get('date', '')}
subject: {email_data.get('subject', '')}
gmail_id: {email_data.get('id', '')}
---

# {email_data.get('subject', 'No Subject')}

**From:** {email_data.get('from', 'Unknown')}
**Date:** {email_data.get('date', '')}

---

{email_data.get('body', email_data.get('snippet', ''))}
"""

        filepath.write_text(content, encoding="utf-8")
        return filepath

    def _check_new_emails(self) -> None:
        """Check for new emails and process them."""
        try:
            # Get list of messages in inbox
            results = self._service.users().messages().list(
                userId="me",
                labelIds=["INBOX"],
                maxResults=10,
            ).execute()

            messages = results.get("messages", [])

            for msg in messages:
                msg_id = msg["id"]

                if msg_id not in self._seen_ids:
                    self._seen_ids.add(msg_id)

                    # Skip initial population (don't alert for existing emails)
                    if self._running:
                        email_data = self._get_email_data(msg_id)
                        self.event_handler.on_new_email(msg_id, email_data)

                        # Save to vault
                        saved_path = self._save_email_to_vault(email_data)
                        print(f"  -> Saved to: {saved_path.name}")

        except HttpError as error:
            print(f"Gmail API error: {error}")

    def start(self) -> None:
        """Start watching Gmail inbox."""
        print("Authenticating with Gmail...")
        creds = self._authenticate()
        self._service = build("gmail", "v1", credentials=creds)

        # Initial population of seen IDs (don't process existing emails)
        print("Loading existing emails...")
        self._check_new_emails()

        self._running = True
        print(f"Watching Gmail inbox (polling every {self.poll_interval}s)")
        print("Press Ctrl+C to stop...")

    def stop(self) -> None:
        """Stop watching."""
        if self._running:
            self._running = False
            print("\nGmail watcher stopped.")

    def run(self) -> None:
        """Run the watcher until interrupted."""
        self.start()
        try:
            while self._running:
                time.sleep(self.poll_interval)
                self._check_new_emails()
        except KeyboardInterrupt:
            self.stop()


def watch(
    credentials_path: str | Path | None = None,
    poll_interval: int = 60,
) -> None:
    """Convenience function to start watching Gmail.

    Args:
        credentials_path: Path to OAuth credentials.json file
        poll_interval: Seconds between polling
    """
    watcher = GmailWatcher(
        credentials_path=credentials_path,
        poll_interval=poll_interval,
    )
    watcher.run()


if __name__ == "__main__":
    watch()
