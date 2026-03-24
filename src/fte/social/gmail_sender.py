"""Gmail Sender - Send emails using Gmail API."""

import base64
import pickle
from pathlib import Path
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scope - for sending emails
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class GmailSender:
    """Send emails using Gmail API."""

    def __init__(
        self,
        credentials_path: str | Path | None = None,
        token_path: str | Path | None = None,
    ):
        """Initialize Gmail sender.

        Args:
            credentials_path: Path to OAuth credentials.json file
            token_path: Path to store/load token.pickle
        """
        base_path = Path(__file__).parent.parent.parent

        if credentials_path is None:
            credentials_path = base_path / "credentials.json"
        if token_path is None:
            # Use a different token file for sending (with different scope)
            token_path = base_path / "token_send.pickle"

        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self._service = None

    def _authenticate(self) -> Credentials:
        """Authenticate with Gmail API for sending.

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

    def _get_service(self):
        """Get or create Gmail service."""
        if self._service is None:
            creds = self._authenticate()
            self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str | None = None,
        bcc: str | None = None,
        is_html: bool = False,
    ) -> dict:
        """Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            cc: Optional CC recipients
            bcc: Optional BCC recipients
            is_html: Whether the body is HTML content

        Returns:
            Dictionary with result (success status, message_id, etc.)
        """
        try:
            service = self._get_service()

            # Create message
            message = EmailMessage()
            message["To"] = to
            message["Subject"] = subject

            if cc:
                message["Cc"] = cc
            if bcc:
                message["Bcc"] = bcc

            if is_html:
                message.set_content(body, subtype="html")
            else:
                message.set_content(body)

            # Encode message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            send_request = {
                "raw": encoded_message
            }

            # Send message
            result = service.users().messages().send(
                userId="me", body=send_request
            ).execute()

            return {
                "success": True,
                "message_id": result.get("id"),
                "thread_id": result.get("threadId"),
                "label_ids": result.get("labelIds", []),
                "to": to,
                "subject": subject,
            }

        except HttpError as error:
            return {
                "success": False,
                "error": str(error),
                "to": to,
                "subject": subject,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "to": to,
                "subject": subject,
            }


def send_email_simple(
    to: str,
    subject: str,
    body: str,
    credentials_path: str | Path | None = None,
) -> dict:
    """Convenience function to send an email.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        credentials_path: Path to OAuth credentials.json file

    Returns:
        Dictionary with result
    """
    sender = GmailSender(credentials_path=credentials_path)
    return sender.send_email(to=to, subject=subject, body=body)


def send_email_html(
    to: str,
    subject: str,
    html_body: str,
    credentials_path: str | Path | None = None,
) -> dict:
    """Convenience function to send an HTML email.

    Args:
        to: Recipient email address
        subject: Email subject
        html_body: HTML email body content
        credentials_path: Path to OAuth credentials.json file

    Returns:
        Dictionary with result
    """
    sender = GmailSender(credentials_path=credentials_path)
    return sender.send_email(to=to, subject=subject, body=html_body, is_html=True)
