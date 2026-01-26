# Company Handbook

This handbook provides comprehensive documentation for the FTE (Foundation Tier) workflow automation system.

---

## Project Overview

FTE is a workflow automation system that combines:
- **Obsidian Vault**: For knowledge management and note organization
- **File System Watcher**: Monitors the Inbox folder for new items
- **Claude Code Agent Skills**: AI-powered automation for processing and categorizing items

### Goals
1. Streamline information capture and processing
2. Automate routine categorization tasks
3. Maintain organized, searchable knowledge base
4. Reduce manual file management overhead

---

## Folder Structure

```
vault/
├── Inbox/           # New items land here automatically
├── Needs_Action/    # Items requiring human attention
├── Done/            # Completed/archived items
├── Dashboard.md     # Central navigation hub
└── Company_Handbook.md  # This file
```

### Inbox
- **Purpose**: Temporary holding area for new items
- **Usage**: Drop files here or let the watcher create them
- **Processing**: Use `/inbox-processor` skill to categorize

### Needs_Action
- **Purpose**: Items requiring human decision or action
- **Usage**: Review and process items here
- **Completion**: Use `/task-manager` to move to Done

### Done
- **Purpose**: Archive of completed items
- **Usage**: Reference for past decisions and actions

---

## Workflow Guidelines

### Standard Workflow
1. **Capture**: New items arrive in Inbox (manually or via watcher)
2. **Process**: Run `/inbox-processor` to analyze and categorize
3. **Action**: Items move to Needs_Action for human review
4. **Complete**: Use `/task-manager` to mark done and archive

### Best Practices
- Process Inbox at least once daily
- Keep Needs_Action list manageable (< 20 items)
- Archive completed items promptly
- Use consistent naming conventions

---

## Tag Conventions

Use tags to categorize and filter notes:

| Tag | Usage |
|-----|-------|
| #urgent | High priority items |
| #review | Needs review before action |
| #reference | Information for future reference |
| #meeting | Meeting notes or agendas |
| #task | Actionable task items |
| #idea | Ideas for future consideration |

---

## Agent Skills Reference

### /inbox-processor
**Purpose**: Analyze and categorize items in Inbox
**Usage**: Run when new items arrive
**Actions**:
- Analyzes content of inbox items
- Suggests categorization
- Moves items to appropriate folders

### /task-manager
**Purpose**: Manage task status and movement
**Usage**: Process items in Needs_Action
**Actions**:
- Update task status
- Move between folders
- Mark items as complete

### /dashboard-updater
**Purpose**: Refresh Dashboard.md statistics
**Usage**: After processing items
**Actions**:
- Count items in each folder
- Update pending counters
- Log recent activity

### /note-creator
**Purpose**: Create structured notes
**Usage**: When capturing new information
**Actions**:
- Create properly formatted notes
- Apply frontmatter metadata
- Place in appropriate folder

---

## CLI Commands

The FTE command-line interface provides these commands:

```bash
# Start file system watcher
uv run fte watch

# Show vault status
uv run fte status

# Process inbox items
uv run fte process
```

---

## File System Watcher

The watcher monitors `vault/Inbox/` for changes:

### Events Detected
- **Created**: New file added to Inbox
- **Modified**: Existing file updated
- **Deleted**: File removed from Inbox

### Configuration
- **Watch Path**: `vault/Inbox/`
- **Recursive**: No (top-level only)
- **File Types**: All files (focus on .md)

---

## Getting Started

1. Open this vault in Obsidian
2. Start the watcher: `uv run fte watch`
3. Add items to Inbox
4. Use Agent Skills to process items
5. Review Dashboard for status

---

## Troubleshooting

### Watcher Not Starting
- Ensure dependencies installed: `uv sync`
- Check vault path exists
- Verify permissions on Inbox folder

### Skills Not Working
- Confirm Claude Code is configured
- Check skill files in `.claude/skills/`
- Review skill documentation

### Dashboard Not Updating
- Run `/dashboard-updater` manually
- Check file permissions
- Verify Dashboard.md exists

---

_Version: 1.0.0 | Bronze Tier Foundation_
