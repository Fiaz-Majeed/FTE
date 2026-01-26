"""Task Manager Skill - Manage task status and movement between folders."""

from pathlib import Path
from ..vault_manager import VaultManager


def move_task(
    file_name: str,
    destination: str,
    vault_path: str | Path | None = None,
) -> dict:
    """Move a task file to a different folder.

    Args:
        file_name: Name of the file to move (with or without .md extension)
        destination: Target folder (Inbox, Needs_Action, Done)
        vault_path: Optional path to vault directory

    Returns:
        Result dictionary with status and new path
    """
    manager = VaultManager(vault_path)

    # Ensure .md extension
    if not file_name.endswith(".md"):
        file_name = f"{file_name}.md"

    # Find the file in any folder
    source_path = None
    for folder in ["Inbox", "Needs_Action", "Done"]:
        potential_path = manager.vault_path / folder / file_name
        if potential_path.exists():
            source_path = potential_path
            break

    if source_path is None:
        return {
            "success": False,
            "error": f"File not found: {file_name}",
        }

    # Validate destination
    valid_destinations = ["Inbox", "Needs_Action", "Done"]
    if destination not in valid_destinations:
        return {
            "success": False,
            "error": f"Invalid destination. Use one of: {valid_destinations}",
        }

    # Move the file
    new_path = manager.move_file(source_path, destination)

    # Update dashboard
    manager.update_dashboard()

    return {
        "success": True,
        "message": f"Moved {file_name} to {destination}",
        "old_path": str(source_path),
        "new_path": str(new_path),
    }


def complete_task(
    file_name: str,
    vault_path: str | Path | None = None,
) -> dict:
    """Mark a task as complete by moving it to Done.

    Args:
        file_name: Name of the file to complete
        vault_path: Optional path to vault directory

    Returns:
        Result dictionary
    """
    return move_task(file_name, "Done", vault_path)


def list_tasks(
    folder: str = "Needs_Action",
    vault_path: str | Path | None = None,
) -> dict:
    """List all tasks in a folder.

    Args:
        folder: Folder to list (default: Needs_Action)
        vault_path: Optional path to vault directory

    Returns:
        Dictionary with task list
    """
    manager = VaultManager(vault_path)
    files = manager.list_files(folder)

    tasks = []
    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        # Get first line after frontmatter as title
        title = file_path.stem
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        tasks.append({
            "name": file_path.stem,
            "title": title,
            "path": str(file_path),
        })

    return {
        "folder": folder,
        "count": len(tasks),
        "tasks": tasks,
    }


def get_task_summary(vault_path: str | Path | None = None) -> str:
    """Get a summary of all tasks across folders.

    Args:
        vault_path: Optional path to vault directory

    Returns:
        Formatted summary string
    """
    manager = VaultManager(vault_path)
    status = manager.get_status()

    lines = [
        "Task Summary",
        "=" * 40,
        f"Inbox:        {status['inbox']} items",
        f"Needs Action: {status['needs_action']} items",
        f"Done:         {status['done']} items",
        "",
    ]

    # List Needs_Action items
    if status["needs_action"] > 0:
        lines.append("Pending Tasks:")
        result = list_tasks("Needs_Action", vault_path)
        for task in result["tasks"]:
            lines.append(f"  - {task['title']}")

    return "\n".join(lines)
