#!/usr/bin/env python3
"""
Interactive Email Review System
Reviews emails in the Inbox folder and allows user to reply to them
"""

import sys
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fte.vault_manager import VaultManager
from fte.skills.task_manager import move_task

def get_email_details(file_path):
    """Extract email details from the markdown file."""
    content = file_path.read_text(encoding='utf-8')

    # Parse frontmatter to get email metadata
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

def send_reply(sender_email, sender_password, recipient_email, subject, reply_body, original_from):
    """Send a reply email."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Re: {subject}"

        # Add reference to original sender
        body = f"On {original_from}, you wrote:\n\n{reply_body}"
        msg.attach(MIMEText(body, 'plain'))

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

def review_and_process_emails():
    """Review emails in Inbox and allow user to reply to them."""
    vault_path = Path("vault")
    inbox_path = vault_path / "Inbox"
    manager = VaultManager(vault_path)

    # Get all email files in Inbox
    email_files = list(inbox_path.glob("*.md"))

    if not email_files:
        print("No emails in Inbox to review.")
        return

    print(f"Found {len(email_files)} emails in Inbox to review:\n")

    for i, email_file in enumerate(email_files, 1):
        print(f"--- Email {i}/{len(email_files)} ---")

        # Get email details
        metadata, body = get_email_details(email_file)

        subject = metadata.get('subject', 'No Subject')
        sender = metadata.get('from', 'Unknown Sender')
        date = metadata.get('date', 'Unknown Date')

        print(f"Subject: {subject}")
        print(f"From: {sender}")
        print(f"Date: {date}")
        print(f"File: {email_file.name}")
        print("\nPreview:")
        print(body[:300] + "..." if len(body) > 300 else body)
        print()

        # Ask user what to do
        while True:
            action = input("Choose action: [r]eply, [m]ove to done, [s]kip, [q]uit: ").lower().strip()

            if action == 'q':
                print("Quitting email review.")
                return
            elif action == 's':
                print("Skipping this email.\n")
                break
            elif action == 'm':
                # Move to Done without replying
                result = move_task(email_file.stem, 'Done')
                if result['success']:
                    print(f"Moved to Done: {result['message']}")
                else:
                    print(f"Error moving to Done: {result['error']}")
                print()
                break
            elif action == 'r':
                # Reply to the email
                print("\nPreparing to reply...")

                # Get email credentials
                sender_email = input("Your email address: ").strip()
                sender_password = getpass("Your email password/app-specific password: ")

                # Get reply content
                print("\nEnter your reply (press Enter twice to finish):")
                reply_lines = []
                empty_line_count = 0

                while empty_line_count < 2:
                    line = input()
                    if line.strip() == "":
                        empty_line_count += 1
                        if empty_line_count < 2:
                            reply_lines.append(line)
                    else:
                        empty_line_count = 0
                        reply_lines.append(line)

                reply_content = "\n".join(reply_lines[:-2])  # Remove the last two empty lines

                if reply_content.strip():
                    # Extract recipient from original email
                    original_recipient = metadata.get('to', '').split('<')[0].strip()

                    if original_recipient and original_recipient != 'Unknown':
                        # Send the reply
                        success = send_reply(
                            sender_email,
                            sender_password,
                            original_recipient,
                            subject,
                            reply_content,
                            sender
                        )

                        if success:
                            # Move to Done after successful reply
                            result = move_task(email_file.stem, 'Done')
                            if result['success']:
                                print(f"After reply, moved to Done: {result['message']}")
                            else:
                                print(f"Error moving to Done after reply: {result['error']}")
                        else:
                            print("Failed to send reply, keeping email in Inbox.")
                    else:
                        print("Could not determine recipient from original email, skipping reply.")
                else:
                    print("No reply content entered, skipping reply.")

                print()
                break
            else:
                print("Invalid option. Please choose [r]eply, [m]ove to done, [s]kip, or [q]uit.")

def main():
    print("Interactive Email Review System")
    print("===============================")
    print("This system will help you review emails in your Inbox and reply to them.")
    print()

    review_and_process_emails()

    print("Email review completed!")

if __name__ == "__main__":
    main()