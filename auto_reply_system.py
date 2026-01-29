#!/usr/bin/env python3
"""
Auto-Reply System
Detects when emails in Needs_Action have responses and sends them automatically
"""

import sys
import os
from pathlib import Path
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass
from datetime import datetime

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

def send_reply(sender_email, sender_password, recipient_email, subject, reply_body, original_from=None):
    """Send a reply email."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Re: {subject}"

        # Format the reply body
        full_body = reply_body
        if original_from:
            full_body = f"Hi,\n\n{full_body}\n\nOn {original_from}, you wrote:\n\n[Original message content]"

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

def check_and_process_replies():
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

                # Get credentials from environment variables or prompt
                sender_email = os.getenv('EMAIL_ADDRESS')
                sender_password = os.getenv('EMAIL_PASSWORD')

                if not sender_email:
                    sender_email = input("Your email address: ")
                if not sender_password:
                    sender_password = getpass("Your email password/app-specific password: ")

                # Send the reply
                success = send_reply(
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

def check_moved_to_done():
    """Check emails that were just moved to Done and process them for sending."""
    vault_path = Path("vault")
    done_path = vault_path / "Done"
    manager = VaultManager(vault_path)

    # Get all email files in Done
    email_files = list(done_path.glob("*.md"))

    if not email_files:
        return

    # Find recently moved files (within last few minutes)
    import time
    current_time = time.time()
    recent_threshold = 300  # 5 minutes

    for email_file in email_files:
        file_modified = email_file.stat().st_mtime
        if current_time - file_modified < recent_threshold:
            print(f"Checking recently moved email: {email_file.name}")

            # Read the file content
            content = email_file.read_text(encoding='utf-8')

            # Extract metadata and body
            metadata, body = extract_email_metadata(content)

            # Look for a response in the content
            response = find_response_in_content(content)

            if response:
                print(f"  Response found in {email_file.name}!")

                # Get sender info from metadata
                original_sender = metadata.get('from', '')
                original_subject = metadata.get('subject', 'No Subject')

                # Extract email address from "Name <email@domain.com>" format
                email_match = re.search(r'<([^>]+)>', original_sender)
                recipient_email = email_match.group(1) if email_match else original_sender

                if recipient_email:
                    print(f"  Preparing to send reply to: {recipient_email}")

                    # Get credentials from environment variables or prompt
                    sender_email = os.getenv('EMAIL_ADDRESS')
                    sender_password = os.getenv('EMAIL_PASSWORD')

                    if not sender_email:
                        sender_email = input("Your email address: ")
                    if not sender_password:
                        sender_password = getpass("Your email password/app-specific password: ")

                    # Send the reply
                    success = send_reply(
                        sender_email,
                        sender_password,
                        recipient_email,
                        original_subject,
                        response,
                        metadata.get('date', 'unknown date')
                    )

                    if success:
                        print(f"  Reply sent successfully for: {email_file.name}")
                    else:
                        print(f"  Failed to send reply for: {email_file.name}")
                else:
                    print(f"  Could not extract recipient email from: {original_sender}")


def manual_check_file(file_path_str):
    """Manually check a specific file for response and send it."""
    file_path = Path(file_path_str)

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    # Read the file content
    content = file_path.read_text(encoding='utf-8')

    # Extract metadata and body
    metadata, body = extract_email_metadata(content)

    # Look for a response in the content
    response = find_response_in_content(content)

    if response:
        print(f"Response found in {file_path.name}!")
        print(f"Response: {response}")

        # Get sender info from metadata
        original_sender = metadata.get('from', '')
        original_subject = metadata.get('subject', 'No Subject')

        # Extract email address from "Name <email@domain.com>" format
        email_match = re.search(r'<([^>]+)>', original_sender)
        recipient_email = email_match.group(1) if email_match else original_sender

        if recipient_email:
            # Get credentials from environment variables or prompt
            sender_email = os.getenv('EMAIL_ADDRESS')
            sender_password = os.getenv('EMAIL_PASSWORD')

            if not sender_email:
                sender_email = input("Your email address: ")
            if not sender_password:
                sender_password = getpass("Your email password/app-specific password: ")

            # Send the reply
            success = send_reply(
                sender_email,
                sender_password,
                recipient_email,
                original_subject,
                response,
                metadata.get('date', 'unknown date')
            )

            if success:
                # Determine original folder and move to Done if not already there
                if file_path.parent.name != 'Done':
                    result = move_task(file_path.stem, 'Done')
                    if result['success']:
                        print(f"Successfully moved to Done: {result['message']}")
                    else:
                        print(f"Error moving to Done: {result['error']}")
            else:
                print("Failed to send reply.")
        else:
            print(f"Could not extract recipient email from: {original_sender}")
    else:
        print(f"No response found in {file_path.name}")

if __name__ == "__main__":
    print("Auto-Reply System")
    print("=================")
    print("This system checks emails in Needs_Action for responses and sends them automatically.")
    print()

    # Check both Needs_Action and Done folders
    check_and_process_replies()
    check_moved_to_done()