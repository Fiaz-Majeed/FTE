---
description: Refresh Dashboard.md with current vault statistics
---

# Dashboard Updater

Refresh Dashboard.md with current vault statistics.

## Usage

Run this skill after processing items to update the Dashboard.md counters.

## Instructions

1. Count files in each folder:
   - `vault/Inbox/` - pending items
   - `vault/Needs_Action/` - active tasks
   - `vault/Done/` - completed items
2. Update Dashboard.md:
   - Update "Inbox: X items" counter
   - Update "Needs Action: X items" counter
   - Update "Completed Today: X items" counter (if tracked)
   - Update "Last updated" timestamp
3. Optionally add recent activity notes

## Dashboard Location

`vault/Dashboard.md`

## Python Module

```python
from fte.skills.dashboard_updater import update_dashboard, get_dashboard_stats
```

## Statistics Tracked

- Total items per folder
- Completion rate (Done / Total)
- Last update timestamp

## Example Output

```
Dashboard Report
========================================
Generated: 2025-01-25 15:30

Current Status:
  Inbox:        3 items
  Needs Action: 5 items
  Done:         12 items

Total items:     20
Completion rate: 60.0%
```
