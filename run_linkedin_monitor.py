#!/usr/bin/env python3
"""Script to run LinkedIn monitoring"""

import os
import sys
from pathlib import Path
import signal
import time

# Add the src directory to the path so we can import fte modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set credentials
os.environ['LINKEDIN_USERNAME'] = 'fiaz.majeed@uog.edu.pk'
os.environ['LINKEDIN_PASSWORD'] = 'UOGFocal0222'

def signal_handler(sig, frame):
    print('\nLinkedIn watcher stopped by user.')
    sys.exit(0)

def main():
    print("Starting LinkedIn Activity Monitor...")
    print("This will watch for new LinkedIn notifications, messages, and comments")
    print("Press Ctrl+C to stop monitoring")

    signal.signal(signal.SIGINT, signal_handler)

    try:
        from fte.watchers.linkedin_watcher import LinkedInWatcher

        print(f"Monitoring LinkedIn account: {os.environ.get('LINKEDIN_USERNAME')}")

        # Create the watcher instance
        watcher = LinkedInWatcher(
            username=os.environ.get("LINKEDIN_USERNAME"),
            password=os.environ.get("LINKEDIN_PASSWORD"),
            poll_interval=300  # Check every 5 minutes
        )

        print("LinkedIn watcher initialized successfully!")
        print("Monitoring for new notifications and messages...")
        print("New activity will be saved to your vault/Inbox/ folder")

        # Run the watcher
        watcher.run()

    except ImportError as e:
        print(f"Error importing LinkedIn watcher: {e}")
    except KeyboardInterrupt:
        print("\nLinkedIn watcher stopped by user.")
    except Exception as e:
        print(f"Error running LinkedIn watcher: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()