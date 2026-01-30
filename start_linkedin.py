#!/usr/bin/env python3
"""Direct startup script for LinkedIn watcher"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import fte modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set credentials if not already set
os.environ.setdefault("LINKEDIN_USERNAME", "fiaz.majeed@uog.edu.pk")
os.environ.setdefault("LINKEDIN_PASSWORD", "UOGFocal0222")

def main():
    try:
        from fte.watchers.linkedin_watcher import LinkedInWatcher

        print("Starting LinkedIn Watcher...")
        print("Username:", os.environ.get("LINKEDIN_USERNAME"))

        # Create the watcher instance
        watcher = LinkedInWatcher(
            username=os.environ.get("LINKEDIN_USERNAME"),
            password=os.environ.get("LINKEDIN_PASSWORD")
        )

        # Run the watcher
        watcher.run()

    except ImportError as e:
        print(f"Error importing LinkedIn watcher: {e}")
        print("Make sure you have installed the linkedin-api package:")
        print("pip install linkedin-api")
    except Exception as e:
        print(f"Error starting LinkedIn watcher: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()