#!/usr/bin/env python3
"""
AI Email Assistant
Monitors the Inbox and automatically generates AI responses to emails
"""

import sys
import time
from pathlib import Path
from datetime import datetime

def monitor_and_respond():
    """Monitor the Inbox and automatically generate AI responses."""
    # Add the src directory to the Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    from fte.vault_manager import VaultManager
    from fte.skills.inbox_processor import process_inbox_with_ai_responses
    from fte.skills.task_manager import move_task

    print("AI Email Assistant Starting...")
    print("Monitoring Inbox for new emails to generate responses...")

    vault_manager = VaultManager()

    while True:
        try:
            # Process inbox to generate AI responses
            results = process_inbox_with_ai_responses()

            if results['summary']['total_inbox_items'] > 0:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"Processed {results['summary']['total_inbox_items']} emails in Inbox")
                print(f"  - AI responses generated: {results['summary']['ai_responses_generated']}")
                print(f"  - AI responses failed: {results['summary']['ai_responses_failed']}")

                # Move processed emails to Needs_Action for review
                inbox_items = vault_manager.list_files('Inbox')
                for item in inbox_items:
                    # Move each processed email to Needs_Action for user review
                    result = move_task(item.stem, 'Needs_Action')
                    if result['success']:
                        print(f"  - Moved {item.name} to Needs_Action for review")
                    else:
                        print(f"  - Error moving {item.name}: {result['error']}")
            else:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"Inbox is empty, no processing needed")

            # Wait for 60 seconds before checking again
            print("Waiting 60 seconds before next check...\n")
            time.sleep(60)

        except KeyboardInterrupt:
            print("\nAI Email Assistant stopped by user.")
            break
        except Exception as e:
            print(f"Error in AI Email Assistant: {e}")
            time.sleep(60)  # Wait before retrying


def process_single_email(file_path):
    """Process a single email file to generate an AI response."""
    import sys
    from pathlib import Path

    # Add the src directory to the Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    from fte.skills.email_response_generator import generate_email_response

    result = generate_email_response(file_path)
    if result['success']:
        print(f"AI response generated for: {result['file_path']}")
    else:
        print(f"Failed to generate response for {file_path}: {result['error']}")

    return result


if __name__ == "__main__":
    monitor_and_respond()