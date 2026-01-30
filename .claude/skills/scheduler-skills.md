# Scheduler Skills

This skill schedules and manages recurring tasks.

## Functions:

### schedule_recurring_task
Schedule a recurring task at regular intervals.
- `task_name`: Name of the task to schedule
- `hours`: Hours between executions (default: 0)
- `minutes`: Minutes between executions (default: 0)
- `seconds`: Seconds between executions (default: 0)
- `description`: Description of the task (optional)
- `vault_path`: Path to vault directory (optional)

### schedule_cron_task
Schedule a task using cron expression.
- `task_name`: Name of the task to schedule
- `cron_expression`: Cron expression (e.g., "0 9 * * 1-5" for 9 AM weekdays)
- `description`: Description of the task (optional)
- `vault_path`: Path to vault directory (optional)

### cancel_scheduled_task
Cancel a scheduled task.
- `task_id`: ID of the task to cancel
- `vault_path`: Path to vault directory (optional)

### get_scheduled_tasks
Get list of scheduled tasks.
- `vault_path`: Path to vault directory (optional)

### get_active_tasks
Get list of active scheduled tasks.
- `vault_path`: Path to vault directory (optional)

### start_scheduler
Start the task scheduler.
- `vault_path`: Path to vault directory (optional)

### schedule_vault_maintenance
Schedule vault maintenance tasks.
- `vault_path`: Path to vault directory (optional)

### schedule_daily_report
Schedule daily report generation.
- `vault_path`: Path to vault directory (optional)

## Usage Examples:

```
/inbox-processor schedule_recurring_task "daily_backup" hours=24 description="Daily backup of vault"
/task-manager schedule_cron_task "weekly_report" "0 9 * * 1" description="Weekly report generation"
/dashboard-updater get_scheduled_tasks
/note-creator schedule_vault_maintenance
```