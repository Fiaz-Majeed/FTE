"""Dashboard Updater Skill - Refresh Dashboard.md with current statistics."""

from pathlib import Path
from datetime import datetime
from ..vault_manager import VaultManager


def update_dashboard(vault_path: str | Path | None = None) -> dict:
    """Update the Dashboard.md with current vault statistics.

    Args:
        vault_path: Optional path to vault directory

    Returns:
        Result dictionary with updated stats
    """
    manager = VaultManager(vault_path)

    if not manager.dashboard_path.exists():
        return {
            "success": False,
            "error": "Dashboard.md not found",
        }

    # Get current status
    status = manager.get_status()

    # Update the dashboard
    manager.update_dashboard()

    return {
        "success": True,
        "message": "Dashboard updated successfully",
        "stats": status,
        "updated_at": datetime.now().isoformat(),
    }


def get_dashboard_stats(vault_path: str | Path | None = None) -> dict:
    """Get current dashboard statistics without updating.

    Args:
        vault_path: Optional path to vault directory

    Returns:
        Dictionary with current stats
    """
    manager = VaultManager(vault_path)
    status = manager.get_status()

    total = status["inbox"] + status["needs_action"] + status["done"]

    return {
        "inbox": status["inbox"],
        "needs_action": status["needs_action"],
        "done": status["done"],
        "total": total,
        "completion_rate": (
            round(status["done"] / total * 100, 1) if total > 0 else 0
        ),
    }


def format_dashboard_report(vault_path: str | Path | None = None) -> str:
    """Generate a formatted dashboard report.

    Args:
        vault_path: Optional path to vault directory

    Returns:
        Formatted report string
    """
    stats = get_dashboard_stats(vault_path)

    lines = [
        "Dashboard Report",
        "=" * 40,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Current Status:",
        f"  Inbox:        {stats['inbox']} items",
        f"  Needs Action: {stats['needs_action']} items",
        f"  Done:         {stats['done']} items",
        "",
        f"Total items:     {stats['total']}",
        f"Completion rate: {stats['completion_rate']}%",
        "",
    ]

    # Add recommendations
    lines.append("Recommendations:")
    if stats["inbox"] > 5:
        lines.append("  - Process inbox items (queue getting large)")
    if stats["needs_action"] > 10:
        lines.append("  - Review pending tasks (many items waiting)")
    if stats["inbox"] == 0 and stats["needs_action"] == 0:
        lines.append("  - All caught up! Great job.")

    return "\n".join(lines)
