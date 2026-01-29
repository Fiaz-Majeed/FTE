#!/usr/bin/env python3
"""
Script to process email tasks from Needs_Action folder.
- Checks the Needs_Action folder for pending email tasks
- Processes them based on content
- Moves completed tasks to Done folder
- Updates the Dashboard
"""

import os
import sys
from pathlib import Path
import shutil
from datetime import datetime
import re

def process_email_tasks():
    """Process pending email tasks in the Needs_Action folder."""

    # Define vault paths
    vault_path = Path("vault")
    needs_action_path = vault_path / "Needs_Action"
    done_path = vault_path / "Done"
    inbox_path = vault_path / "Inbox"
    dashboard_path = vault_path / "Dashboard.md"

    # Ensure directories exist
    needs_action_path.mkdir(parents=True, exist_ok=True)
    done_path.mkdir(parents=True, exist_ok=True)

    print("Checking Needs_Action folder for pending email tasks...")

    # Get all markdown files in Needs_Action folder
    needs_action_files = list(needs_action_path.glob("*.md"))

    if not needs_action_files:
        print("No pending tasks in Needs_Action folder.")

        # Check if there are any emails in Inbox that might need to be moved to Needs_Action
        inbox_files = list(inbox_path.glob("*.md"))
        if inbox_files:
            print(f"Found {len(inbox_files)} items in Inbox. Some may need processing.")

            # For demonstration, let's move some emails that seem to require action to Needs_Action
            for email_file in inbox_files:
                content = email_file.read_text(encoding='utf-8')

                # Determine if this email requires action based on certain keywords
                requires_action = any(keyword.lower() in content.lower() for keyword in [
                    'urgent', 'action required', 'meeting', 'request', 'need', 'help', 'assistance'
                ])

                if requires_action:
                    print(f"Moving {email_file.name} to Needs_Action (requires action)")
                    new_path = needs_action_path / email_file.name
                    shutil.move(str(email_file), str(new_path))
                    needs_action_files.append(new_path)

    processed_count = 0

    # Process each file in Needs_Action
    for task_file in needs_action_files:
        print(f"\nProcessing: {task_file.name}")

        # Read the file content
        content = task_file.read_text(encoding='utf-8')

        # Determine if the task is complete based on content analysis
        is_complete = analyze_task_completion(content)

        if is_complete:
            print(f"  Task appears complete. Moving to Done folder...")

            # Move to Done folder
            done_file_path = done_path / task_file.name
            shutil.move(str(task_file), str(done_file_path))

            # Update the file to mark as completed
            update_completed_task(done_file_path)

            processed_count += 1
        else:
            print(f"  Task still requires action. Keeping in Needs_Action.")

    print(f"\nProcessed {processed_count} completed tasks.")

    # Update dashboard with new statistics
    update_dashboard(dashboard_path, vault_path)

    print("Dashboard updated successfully.")

    # Print final status
    print_status(vault_path)


def analyze_task_completion(content):
    """
    Analyze if a task is complete based on its content.
    This is a simplified version - in reality, this could involve more complex logic
    like checking for specific completion indicators, responses to requests, etc.
    """
    # For demonstration purposes, we'll say a task is complete if it contains
    # certain indicators that suggest action has been taken
    lower_content = content.lower()

    # Common indicators that a task might be complete
    completion_indicators = [
        'completed', 'done', 'finished', 'resolved', 'addressed',
        'acknowledged', 'responded', 'handled', 'taken care of'
    ]

    # Check if any completion indicators are in the content
    for indicator in completion_indicators:
        if indicator in lower_content:
            return True

    # Special handling for Google verification emails - these are notifications that don't require action
    if 'google account' in lower_content and 'verification' in lower_content and 'protected' in lower_content:
        # Check if it's NOT asking for any explicit action
        # Look for phrases that explicitly request action, but not just mentioning them
        explicit_action_requests = [
            'please ', 'click here', 'you need to', 'you must', 'required: ', 'urgent: ',
            'immediate action', 'required action', 'action required:', 'action required.',
            'reply to this', 'respond to this', 'immediately', 'as soon as possible'
        ]

        # Check for explicit action requests (being more specific to avoid false positives)
        has_explicit_request = False
        for request in explicit_action_requests:
            if request in lower_content:
                has_explicit_request = True
                break

        # If it's just informing about verification and doesn't ask for explicit action, it's processed
        if not has_explicit_request:
            return True

    # Types of emails that typically just need acknowledgment (can be moved to Done)
    notification_types = [
        'verification turned on', 'confirmed', 'activated', 'notification', 'receipt',
        'delivered', 'shipped', 'password reset', 'security alert'
    ]

    # Types of emails that typically require action (should stay in Needs_Action)
    action_required_types = [
        'urgent:', 'meeting', 'request:', 'need help', 'assistance', 'response needed',
        'reply required', 'follow up', 'please ', 'contact ', 'call ', 'schedule ',
        'submit ', 'complete this', 'action required:'
    ]

    # Check if it's a notification type email that doesn't require action
    has_notification_keyword = any(keyword in lower_content for keyword in notification_types)

    # Check for action required keywords, being more specific
    has_action_required_keyword = False
    for keyword in action_required_types:
        if keyword in lower_content:
            has_action_required_keyword = True
            break

    # If it's a notification AND doesn't require specific action, consider it complete
    if has_notification_keyword and not has_action_required_keyword:
        return True

    # If it's clearly requesting action, it's not complete
    if has_action_required_keyword:
        return False

    # For LinkedIn demo content, check if it has been posted already
    if 'linkedin' in lower_content and ('posted' in lower_content or 'published' in lower_content):
        return True

    return False


def update_completed_task(file_path):
    """Update a task file to mark it as completed."""
    content = file_path.read_text(encoding='utf-8')

    # Add completion metadata to the frontmatter if it exists
    if content.startswith('---'):
        # Find the end of the frontmatter section (second occurrence of ---)
        # First, find the first --- (start of frontmatter)
        first_dash = content.find('---')
        if first_dash != -1:
            # Then find the end of the frontmatter (second ---)
            second_dash = content.find('---', first_dash + 3)
            if second_dash != -1:
                # Extract the frontmatter content between the dashes
                frontmatter_content = content[first_dash + 3:second_dash].rstrip()

                # Check if completion date is already in frontmatter
                if 'completed:' not in frontmatter_content:
                    # Add completion date to frontmatter
                    frontmatter_content = frontmatter_content.rstrip() + f"\ncompleted: {datetime.now().isoformat()}\n"

                # Get the rest of the content after the closing ---
                rest_content = content[second_dash + 3:]

                # Reconstruct the file with proper formatting
                new_content = f"---{frontmatter_content}---\n{rest_content.lstrip()}"
                file_path.write_text(new_content, encoding='utf-8')
    else:
        # If no frontmatter, add it at the beginning
        new_content = f"""---
completed: {datetime.now().isoformat()}
---
{content}"""
        file_path.write_text(new_content, encoding='utf-8')


def update_dashboard(dashboard_path, vault_path):
    """Update the dashboard with current statistics."""
    if not dashboard_path.exists():
        print(f"Dashboard file not found: {dashboard_path}")
        return

    # Count files in each folder
    inbox_count = len(list((vault_path / "Inbox").glob("*.md")))
    needs_action_count = len(list((vault_path / "Needs_Action").glob("*.md")))
    done_count = len(list((vault_path / "Done").glob("*.md")))

    content = dashboard_path.read_text(encoding='utf-8')

    # Update counts in the dashboard
    content = re.sub(
        r'\*\*Inbox:\*\* \d+ items',
        f'**Inbox:** {inbox_count} items',
        content
    )

    content = re.sub(
        r'\*\*Needs Action:\*\* \d+ items',
        f'**Needs Action:** {needs_action_count} items',
        content
    )

    # Update the "Completed Today" count by checking recent done items
    # For simplicity, we'll just update the total done count
    content = re.sub(
        r'\*\*Completed Today:\*\* \d+ items',
        f'**Completed Today:** {done_count} items',
        content
    )

    # Update last updated timestamp
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = re.sub(
        r'_Last updated: .*_',
        f'_Last updated: {today}_',
        content
    )

    # Write updated content back to dashboard
    dashboard_path.write_text(content, encoding='utf-8')


def print_status(vault_path):
    """Print current status of all folders."""
    inbox_count = len(list((vault_path / "Inbox").glob("*.md")))
    needs_action_count = len(list((vault_path / "Needs_Action").glob("*.md")))
    done_count = len(list((vault_path / "Done").glob("*.md")))

    print(f"\n--- Current Status ---")
    print(f"Inbox:        {inbox_count} items")
    print(f"Needs Action: {needs_action_count} items")
    print(f"Done:         {done_count} items")


if __name__ == "__main__":
    process_email_tasks()