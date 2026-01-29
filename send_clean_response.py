#!/usr/bin/env python3
"""
Modified Auto-Reply System
This version sends responses without adding 'Hi,' prefix
"""

import sys
import os
from pathlib import Path
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import argparse

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fte.vault_manager import VaultManager
from fte.skills.task_manager import move_task

def extract_email_metadata(content):
    """Extract email metadata from markdown file."""
    if content.startswith('---'):
        end_frontmatter = content.find('---', 3)
        if end_frontmatter != -1:
            frontmatter = content[3:end_frontmatter]

            # Extract metadata
            metadata = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip().strip('"\'')

            # Extract body content after frontmatter
            body = content[end_frontmatter + 3:].strip()
            return metadata, body

    return {}, content

def find_response_in_content(content):
    """Look for responses (user or AI-generated) in the email content."""
    # Look for AI-generated response sections first
    ai_response_marker = "---\n**AI Generated Response**"
    ai_response_pos = content.find(ai_response_marker)

    if ai_response_pos != -1:
        # Extract the AI-generated response
        start_pos = content.find("\n", ai_response_pos)  # Skip the marker line
        if start_pos != -1:
            end_pos = content.find("\n---\n", start_pos)
            if end_pos != -1:
                response = content[start_pos:end_pos].strip()

                # Remove the **AI Generated Response** timestamp line and any title lines
                lines = response.split('\n')
                clean_lines = []
                for line in lines:
                    if not line.strip().startswith("**AI Generated Response**") and \
                       not line.strip().startswith("**Response to"):
                        clean_lines.append(line)

                response = '\n'.join(clean_lines).strip()
                return response

    # If no AI response found, look for our custom response marker
    custom_response_marker = "---\n**Response to"
    custom_response_pos = content.find(custom_response_marker)

    if custom_response_pos != -1:
        # Extract our custom response
        start_pos = content.find("\n", custom_response_pos)
        if start_pos != -1:
            # Find the end of the response
            remaining_content = content[start_pos:]
            lines = remaining_content.split('\n')
            response_lines = []

            # Skip the first line (which is the marker line itself)
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    # Found the closing marker, stop here
                    break
                else:
                    response_lines.append(line)

            response = '\n'.join(response_lines).strip()
            return response

    # If no AI response found, look for common patterns that indicate a user response
    lines = content.split('\n')

    # Look for separator lines or common response markers
    response_start = -1
    for i, line in enumerate(lines):
        # Look for common response indicators
        if line.strip().lower().startswith('> ') or \
           'wrote:' in line or \
           'on ' in line and 'you said' in line or \
           'response:' in line.lower() or \
           line.strip() == '--' or \
           'regards,' in line.lower() or \
           'thanks,' in line.lower() or \
           'best,' in line.lower():
            response_start = i
            break

    if response_start != -1:
        response = '\n'.join(lines[response_start:])
        return response.strip()

    return None

def send_reply_without_hi(sender_email, sender_password, recipient_email, subject, reply_body, original_from=None):
    """Send a reply email without adding 'Hi,' prefix."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Re: {subject}"

        # Use the reply body as-is without adding "Hi,"
        full_body = reply_body

        # If we have the original sender info, we can add a reference
        if original_from:
            full_body += f"\n\nOn {original_from}, you wrote:\n\n[Original message content]"

        msg.attach(MIMEText(full_body, 'plain'))

        # Connect to server and send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()

        print(f"Reply sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def check_and_process_replies(sender_email, sender_password):
    """Check emails in Needs_Action for responses and process them."""
    vault_path = Path("vault")
    needs_action_path = vault_path / "Needs_Action"
    done_path = vault_path / "Done"
    manager = VaultManager(vault_path)

    # Get all email files in Needs_Action
    email_files = list(needs_action_path.glob("*.md"))

    if not email_files:
        print("No emails in Needs_Action to process.")
        return

    print(f"Found {len(email_files)} emails in Needs_Action to check for responses:")

    for email_file in email_files:
        print(f"\nChecking: {email_file.name}")

        # Read the file content
        content = email_file.read_text(encoding='utf-8')

        # Extract metadata and body
        metadata, body = extract_email_metadata(content)

        # Look for a response in the content
        response = find_response_in_content(content)

        if response:
            print(f"  Response found in {email_file.name}!")
            print(f"  Response preview: {response[:100]}...")

            # Get sender info from metadata
            original_sender = metadata.get('from', '')
            original_subject = metadata.get('subject', 'No Subject')

            # Extract email address from "Name <email@domain.com>" format
            email_match = re.search(r'<([^>]+)>', original_sender)
            recipient_email = email_match.group(1) if email_match else original_sender

            if recipient_email:
                print(f"  Preparing to send reply to: {recipient_email}")

                # Send the reply without adding "Hi,"
                success = send_reply_without_hi(
                    sender_email,
                    sender_password,
                    recipient_email,
                    original_subject,
                    response,
                    metadata.get('date', 'unknown date')
                )

                if success:
                    # Move to Done after successful reply
                    result = move_task(email_file.stem, 'Done')
                    if result['success']:
                        print(f"  Successfully moved to Done: {result['message']}")
                    else:
                        print(f"  Error moving to Done: {result['error']}")
                else:
                    print("  Failed to send reply, keeping email in Needs_Action.")
            else:
                print(f"  Could not extract recipient email from: {original_sender}")
        else:
            print(f"  No response found in {email_file.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Auto-Reply System without "Hi," prefix')
    parser.add_argument('--email', required=True, help='Sender email address')
    parser.add_argument('--password', required=True, help='Sender email password or app-specific password')

    args = parser.parse_args()

    print("Auto-Reply System (without 'Hi,' prefix)")
    print("=" * 45)
    print("This system checks emails in Needs_Action for responses and sends them without adding 'Hi,'.")
    print()

    # Process emails with provided credentials
    check_and_process_replies(args.email, args.password)