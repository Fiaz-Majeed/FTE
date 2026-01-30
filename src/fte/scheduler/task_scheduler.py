"""Task Scheduler - Schedule and manage recurring tasks."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import threading

from ..vault_manager import VaultManager


class TaskScheduler:
    """Schedule and manage recurring tasks."""

    def __init__(self, vault_path: str | Path | None = None):
        """Initialize the task scheduler.

        Args:
            vault_path: Path to vault directory
        """
        self.base_path = Path(__file__).parent.parent.parent
        if vault_path is None:
            self.vault_path = self.base_path / "vault"
        else:
            self.vault_path = Path(vault_path)

        self.vault_manager = VaultManager(self.vault_path)
        self.scheduler = BackgroundScheduler()
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self._running = False

        # Load any existing scheduled tasks
        self._load_schedule_state()

    def start(self):
        """Start the scheduler."""
        if not self._running:
            self.scheduler.start()
            self._running = True
            print("Task scheduler started.")

    def stop(self):
        """Stop the scheduler."""
        if self._running:
            self.scheduler.shutdown()
            self._running = False
            print("Task scheduler stopped.")

    def schedule_task(
        self,
        task_name: str,
        func: Callable,
        trigger_type: str,  # 'interval', 'cron', 'date'
        trigger_args: Dict[str, Any],
        args: Optional[tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        description: str = "",
        persist: bool = True
    ) -> str:
        """Schedule a task.

        Args:
            task_name: Name of the task
            func: Function to execute
            trigger_type: Type of trigger ('interval', 'cron', 'date')
            trigger_args: Arguments for the trigger
            args: Arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            description: Description of the task
            persist: Whether to save the task to persistent storage

        Returns:
            Scheduled task ID
        """
        task_id = f"{task_name}_{int(datetime.now().timestamp())}"

        # Create trigger based on type
        if trigger_type == 'interval':
            trigger = IntervalTrigger(**trigger_args)
        elif trigger_type == 'cron':
            trigger = CronTrigger(**trigger_args)
        elif trigger_type == 'date':
            from apscheduler.triggers.date import DateTrigger
            trigger = DateTrigger(**trigger_args)
        else:
            raise ValueError(f"Invalid trigger type: {trigger_type}")

        # Schedule the job
        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            args=args,
            kwargs=kwargs
        )

        # Store task info
        task_info = {
            "id": task_id,
            "name": task_name,
            "function": f"{func.__module__}.{func.__name__}",
            "trigger_type": trigger_type,
            "trigger_args": trigger_args,
            "args": args or (),
            "kwargs": kwargs or {},
            "description": description,
            "scheduled_at": datetime.now().isoformat(),
            "status": "active",
            "persist": persist,
            "job": job
        }

        self.scheduled_tasks[task_id] = task_info

        # Save to persistent storage if requested
        if persist:
            self._save_schedule_state()

        return task_id

    def schedule_recurring_task(
        self,
        task_name: str,
        func: Callable,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        args: Optional[tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        description: str = "",
        persist: bool = True
    ) -> str:
        """Schedule a recurring task at regular intervals.

        Args:
            task_name: Name of the task
            func: Function to execute
            hours: Hours between executions
            minutes: Minutes between executions
            seconds: Seconds between executions
            args: Arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            description: Description of the task
            persist: Whether to save the task to persistent storage

        Returns:
            Scheduled task ID
        """
        trigger_args = {}
        if hours > 0:
            trigger_args["hours"] = hours
        if minutes > 0:
            trigger_args["minutes"] = minutes
        if seconds > 0:
            trigger_args["seconds"] = seconds

        return self.schedule_task(
            task_name=task_name,
            func=func,
            trigger_type="interval",
            trigger_args=trigger_args,
            args=args,
            kwargs=kwargs,
            description=description,
            persist=persist
        )

    def schedule_cron_task(
        self,
        task_name: str,
        func: Callable,
        cron_expression: str,
        args: Optional[tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        description: str = "",
        persist: bool = True
    ) -> str:
        """Schedule a task using cron expression.

        Args:
            task_name: Name of the task
            func: Function to execute
            cron_expression: Cron expression (e.g., "0 9 * * 1-5" for 9 AM weekdays)
            args: Arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            description: Description of the task
            persist: Whether to save the task to persistent storage

        Returns:
            Scheduled task ID
        """
        # Parse cron expression: minute hour day month day_of_week
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have 5 parts: minute hour day month day_of_week")

        trigger_args = {
            "minute": parts[0],
            "hour": parts[1],
            "day": parts[2],
            "month": parts[3],
            "day_of_week": parts[4]
        }

        return self.schedule_task(
            task_name=task_name,
            func=func,
            trigger_type="cron",
            trigger_args=trigger_args,
            args=args,
            kwargs=kwargs,
            description=description,
            persist=persist
        )

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task.

        Args:
            task_id: ID of the task to cancel

        Returns:
            True if task was cancelled successfully
        """
        if task_id in self.scheduled_tasks:
            try:
                self.scheduler.remove_job(task_id)
                self.scheduled_tasks[task_id]["status"] = "cancelled"
                self._save_schedule_state()
                return True
            except Exception:
                # Job might have already run
                self.scheduled_tasks[task_id]["status"] = "cancelled"
                self._save_schedule_state()
                return True

        return False

    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get list of scheduled tasks.

        Returns:
            List of scheduled tasks
        """
        return [
            {k: v for k, v in task.items() if k != 'job'}  # Exclude job objects
            for task in self.scheduled_tasks.values()
        ]

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get list of active scheduled tasks.

        Returns:
            List of active scheduled tasks
        """
        return [
            {k: v for k, v in task.items() if k != 'job'}
            for task in self.scheduled_tasks.values()
            if task["status"] == "active"
        ]

    def _save_schedule_state(self):
        """Save current schedule state to file."""
        state_file = self.vault_path / "task_schedule.json"

        # Prepare state without job objects (which aren't serializable)
        state = {
            "tasks": [
                {k: v for k, v in task.items() if k != 'job'}
                for task in self.scheduled_tasks.values()
                if task.get("persist", False)
            ],
            "last_updated": datetime.now().isoformat(),
        }

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, default=str)

    def _load_schedule_state(self):
        """Load schedule state from file."""
        state_file = self.vault_path / "task_schedule.json"

        if not state_file.exists():
            return

        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Reschedule persisted tasks
            for task_data in state.get("tasks", []):
                if task_data.get("status") == "active":
                    # We can't restore the original function from its name alone
                    # In a real implementation, you'd need to register the functions
                    # For now, we'll just store the task data
                    task_id = task_data["id"]
                    self.scheduled_tasks[task_id] = task_data

        except Exception as e:
            print(f"Error loading schedule state: {e}")

    def run_scheduled_vault_maintenance(self):
        """Run scheduled vault maintenance tasks."""
        print(f"[{datetime.now()}] Running vault maintenance...")

        # Example maintenance tasks:
        # 1. Update dashboard statistics
        try:
            self.vault_manager.update_dashboard()
            print("  - Dashboard updated")
        except Exception as e:
            print(f"  - Error updating dashboard: {e}")

        # 2. Archive old files (move from Done to Archive after 30 days)
        try:
            archive_path = self.vault_path / "Archive"
            archive_path.mkdir(exist_ok=True)

            done_path = self.vault_path / "Done"
            if done_path.exists():
                cutoff_date = datetime.now() - timedelta(days=30)

                for file_path in done_path.glob("*.md"):
                    if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_date:
                        # Move to archive
                        archive_file = archive_path / file_path.name
                        file_path.rename(archive_file)
                        print(f"  - Archived: {file_path.name}")

        except Exception as e:
            print(f"  - Error archiving old files: {e}")

        # 3. Generate daily report
        try:
            status = self.vault_manager.get_status()
            report_content = f"""---
type: daily_report
date: {datetime.now().date().isoformat()}
---

# Daily Vault Report - {datetime.now().date().isoformat()}

## Status
- Inbox: {status['inbox']} items
- Needs Action: {status['needs_action']} items
- Done: {status['done']} items

## Generated
Report generated at {datetime.now().isoformat()}
"""

            report_path = self.vault_path / "Inbox" / f"daily_report_{datetime.now().strftime('%Y%m%d')}.md"
            report_path.write_text(report_content, encoding="utf-8")
            print(f"  - Daily report generated: {report_path.name}")

        except Exception as e:
            print(f"  - Error generating daily report: {e}")

    def run_scheduled_linkedin_posting(self):
        """Run scheduled LinkedIn posting tasks."""
        print(f"[{datetime.now()}] Checking for scheduled LinkedIn posts...")

        # This would integrate with the LinkedIn posting functionality
        # For now, just a placeholder
        print("  - LinkedIn posting check completed")


def create_default_scheduler(vault_path: str | Path | None = None) -> TaskScheduler:
    """Create a scheduler with default tasks.

    Args:
        vault_path: Path to vault directory

    Returns:
        Configured TaskScheduler instance
    """
    scheduler = TaskScheduler(vault_path=vault_path)

    # Schedule default maintenance tasks
    # Run vault maintenance every day at 2 AM
    scheduler.schedule_cron_task(
        task_name="vault_maintenance",
        func=scheduler.run_scheduled_vault_maintenance,
        cron_expression="0 2 * * *",  # Every day at 2:00 AM
        description="Daily vault maintenance and cleanup"
    )

    # Run LinkedIn posting check every hour
    scheduler.schedule_recurring_task(
        task_name="linkedin_check",
        func=scheduler.run_scheduled_linkedin_posting,
        hours=1,
        description="Hourly check for scheduled LinkedIn posts"
    )

    return scheduler