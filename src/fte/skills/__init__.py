"""FTE Agent Skills - AI-powered automation for vault management."""

from .inbox_processor import process_inbox
from .task_manager import move_task, complete_task, list_tasks
from .dashboard_updater import update_dashboard
from .note_creator import create_note

__all__ = [
    "process_inbox",
    "move_task",
    "complete_task",
    "list_tasks",
    "update_dashboard",
    "create_note",
]
