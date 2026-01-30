#!/usr/bin/env python3
"""Script to run the task scheduler"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import fte modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    print("Starting Task Scheduler...")
    print("="*50)

    try:
        from fte.scheduler.task_scheduler import create_default_scheduler

        print("Initializing scheduler...")
        scheduler = create_default_scheduler()

        print("Starting scheduler...")
        scheduler.start()

        print("Scheduler is running with default tasks:")
        print("- Vault maintenance (daily at 2 AM)")
        print("- LinkedIn posting check (every hour)")

        # Show currently scheduled tasks
        active_tasks = scheduler.get_active_tasks()
        print(f"\nActive tasks: {len(active_tasks)}")

        for task in active_tasks:
            print(f"  - {task['name']}: {task['description']}")

        print("\nScheduler is monitoring and will execute scheduled tasks...")
        print("Press Ctrl+C to stop the scheduler")

        # Keep the scheduler running
        import time
        try:
            while True:
                time.sleep(10)  # Check every 10 seconds
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
            scheduler.stop()
            print("Scheduler stopped.")

    except ImportError as e:
        print(f"Error importing scheduler: {e}")
    except Exception as e:
        print(f"Error running scheduler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()