---
description: Analyze and categorize items in the vault Inbox folder
---

# Inbox Processor

Analyze and categorize items in the vault Inbox folder.

## Usage

Run this skill when new items arrive in the Inbox and need processing.

## Instructions

1. Read all markdown files in `vault/Inbox/`
2. For each file, analyze:
   - Title/filename for context
   - Content for urgency indicators (urgent, asap, deadline, critical)
   - Content for task indicators (todo, action, review)
   - Content type (meeting notes, reference, task)
3. Suggest appropriate categorization:
   - **Urgent items**: Move to Needs_Action immediately
   - **Task items**: Move to Needs_Action
   - **Reference material**: Consider moving to Done
   - **Meeting notes**: Extract action items, then move appropriately
4. Present findings to user with recommendations
5. After user approval, move files using the vault_manager module
6. Update Dashboard.md with new statistics

## File Locations

- Inbox: `vault/Inbox/`
- Needs Action: `vault/Needs_Action/`
- Done: `vault/Done/`
- Dashboard: `vault/Dashboard.md`

## Python Module

```python
from fte.skills.inbox_processor import process_inbox, get_inbox_summary
```
