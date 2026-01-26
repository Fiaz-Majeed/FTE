"""Note Creator Skill - Create structured notes in the vault."""

from pathlib import Path
from datetime import datetime
from ..vault_manager import VaultManager


def create_note(
    title: str,
    content: str,
    folder: str = "Inbox",
    tags: list[str] | None = None,
    vault_path: str | Path | None = None,
) -> dict:
    """Create a new note in the vault.

    Args:
        title: Note title
        content: Note body content
        folder: Target folder (default: Inbox)
        tags: Optional list of tags
        vault_path: Optional path to vault directory

    Returns:
        Result dictionary with created note path
    """
    manager = VaultManager(vault_path)

    # Validate folder
    valid_folders = ["Inbox", "Needs_Action", "Done"]
    if folder not in valid_folders:
        return {
            "success": False,
            "error": f"Invalid folder. Use one of: {valid_folders}",
        }

    # Create the note
    note_path = manager.create_note(title, content, folder, tags)

    # Update dashboard
    manager.update_dashboard()

    return {
        "success": True,
        "message": f"Created note: {title}",
        "path": str(note_path),
        "folder": folder,
        "tags": tags or [],
    }


def create_task_note(
    title: str,
    description: str,
    priority: str = "normal",
    due_date: str | None = None,
    vault_path: str | Path | None = None,
) -> dict:
    """Create a task-formatted note.

    Args:
        title: Task title
        description: Task description
        priority: Priority level (low, normal, high, urgent)
        due_date: Optional due date string
        vault_path: Optional path to vault directory

    Returns:
        Result dictionary
    """
    # Build task content
    lines = [
        description,
        "",
        "## Details",
        f"- **Priority:** {priority}",
        f"- **Created:** {datetime.now().strftime('%Y-%m-%d')}",
    ]

    if due_date:
        lines.append(f"- **Due:** {due_date}")

    lines.extend([
        "",
        "## Checklist",
        "- [ ] Task item 1",
        "- [ ] Task item 2",
        "",
        "## Notes",
        "_Add notes here_",
    ])

    content = "\n".join(lines)

    # Set tags based on priority
    tags = ["task"]
    if priority == "urgent":
        tags.append("urgent")
    elif priority == "high":
        tags.append("important")

    return create_note(
        title=title,
        content=content,
        folder="Needs_Action",
        tags=tags,
        vault_path=vault_path,
    )


def create_meeting_note(
    title: str,
    attendees: list[str] | None = None,
    agenda: list[str] | None = None,
    vault_path: str | Path | None = None,
) -> dict:
    """Create a meeting note template.

    Args:
        title: Meeting title
        attendees: List of attendee names
        agenda: List of agenda items
        vault_path: Optional path to vault directory

    Returns:
        Result dictionary
    """
    lines = [
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
    ]

    if attendees:
        lines.append("## Attendees")
        for person in attendees:
            lines.append(f"- {person}")
        lines.append("")

    if agenda:
        lines.append("## Agenda")
        for item in agenda:
            lines.append(f"1. {item}")
        lines.append("")

    lines.extend([
        "## Discussion Notes",
        "_Notes from the meeting_",
        "",
        "## Action Items",
        "- [ ] Action item 1",
        "- [ ] Action item 2",
        "",
        "## Follow-up",
        "_Next steps and follow-up items_",
    ])

    content = "\n".join(lines)

    return create_note(
        title=title,
        content=content,
        folder="Inbox",
        tags=["meeting"],
        vault_path=vault_path,
    )


def quick_capture(
    text: str,
    vault_path: str | Path | None = None,
) -> dict:
    """Quickly capture a note with auto-generated title.

    Args:
        text: Note content
        vault_path: Optional path to vault directory

    Returns:
        Result dictionary
    """
    # Generate title from timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    title = f"Quick Note {timestamp}"

    # Use first line as title if it looks like a title
    first_line = text.split("\n")[0].strip()
    if len(first_line) < 60 and not first_line.startswith("-"):
        title = first_line
        text = "\n".join(text.split("\n")[1:]).strip()

    return create_note(
        title=title,
        content=text,
        folder="Inbox",
        vault_path=vault_path,
    )
