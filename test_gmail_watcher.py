#!/usr/bin/env python3
"""Test script to verify Gmail watcher functionality"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fte.gmail_watcher import GmailWatcher
import time

def test_watcher():
    print("Creating Gmail watcher...")

    # Create watcher instance
    watcher = GmailWatcher(poll_interval=30)  # Check every 30 seconds

    print("Starting Gmail watcher...")
    print("This will authenticate with Gmail and begin watching for new emails.")
    print("New emails will be saved to vault/Inbox/")

    try:
        watcher.start()  # Start without the infinite loop

        # Just run one check to see if it works
        print("\nChecking for new emails once...")
        watcher._check_new_emails()

        print("One-time check completed. Emails would be saved to vault/Inbox/ if any were found.")

        # Keep running to watch for new emails
        print(f"\nNow watching for new emails (checking every {watcher.poll_interval}s)...")
        print("Press Ctrl+C to stop...")

        try:
            while watcher._running:
                time.sleep(watcher.poll_interval)
                watcher._check_new_emails()
        except KeyboardInterrupt:
            print("\nStopping Gmail watcher...")
            watcher.stop()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_watcher()