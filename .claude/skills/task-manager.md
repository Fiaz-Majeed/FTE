---
description: Manage task status and movement between vault folders
---

# Task Manager

Manage task status and movement between vault folders.

## Usage

Run this skill to move tasks between folders or mark them as complete.

## Instructions

1. List current tasks using `vault_manager.list_files()` for each folder
2. Present task status to user
3. Based on user request:
   - **Move task**: Use `vault_manager.move_file(source, destination)`
   - **Complete task**: Move to `Done` folder
   - **Reopen task**: Move back to `Needs_Action`
4. Update Dashboard.md after any changes

## Commands

- Move a file: Specify source file and destination folder
- Complete task: Move file to Done
- List tasks: Show all tasks in a specific folder
- Get summary: Show counts across all folders

## Folder Structure

| Folder | Purpose |
|--------|---------|
| Inbox | New items awaiting processing |
| Needs_Action | Active tasks requiring attention |
| Done | Completed/archived items |

## Python Module

```python
from fte.skills.task_manager import move_task, complete_task, list_tasks
```

## Examples

Move task to Needs_Action:
```python
move_task("my-task.md", "Needs_Action")
```

Complete a task:
```python
complete_task("finished-task.md")
```
