---
description: Create structured notes in the vault
---

# Note Creator

Create structured notes in the vault.

## Usage

Run this skill when you need to create a new note with proper formatting.

## Instructions

1. Gather note details from user:
   - Title (required)
   - Content (required)
   - Target folder (default: Inbox)
   - Tags (optional)
2. Generate frontmatter:
   ```yaml
   ---
   title: Note Title
   created: 2025-01-25T15:30:00
   tags: [tag1, tag2]
   ---
   ```
3. Create the note file in the target folder
4. Update Dashboard.md

## Note Types

### Quick Note
Fast capture with auto-generated title:
```python
quick_capture("Note content here")
```

### Task Note
Structured task with checklist:
```python
create_task_note(
    title="Task Title",
    description="What needs to be done",
    priority="high",  # low, normal, high, urgent
    due_date="2025-01-30"
)
```

### Meeting Note
Meeting template with attendees and agenda:
```python
create_meeting_note(
    title="Team Standup",
    attendees=["Alice", "Bob"],
    agenda=["Updates", "Blockers", "Next steps"]
)
```

## Python Module

```python
from fte.skills.note_creator import create_note, create_task_note, quick_capture
```

## File Naming

- Titles are sanitized for safe filenames
- Special characters removed: `<>:"/\|?*`
- Maximum length: 100 characters
