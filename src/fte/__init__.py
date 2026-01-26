"""FTE - Foundation Tier workflow automation with Obsidian vault integration."""

import sys
from pathlib import Path

from .vault_manager import VaultManager
from .watcher import VaultWatcher, watch


def cmd_watch() -> None:
    """Start the file system watcher."""
    print("FTE Vault Watcher")
    print("=" * 40)
    watch()


def cmd_status() -> None:
    """Show vault status."""
    manager = VaultManager()
    status = manager.get_status()

    print("FTE Vault Status")
    print("=" * 40)
    print(f"Inbox:        {status['inbox']} items")
    print(f"Needs Action: {status['needs_action']} items")
    print(f"Done:         {status['done']} items")
    print("=" * 40)


def cmd_process() -> None:
    """Process items in the Inbox."""
    manager = VaultManager()
    items = manager.get_inbox_items()

    if not items:
        print("Inbox is empty. Nothing to process.")
        return

    print("FTE Inbox Processor")
    print("=" * 40)
    print(f"Found {len(items)} items in Inbox:\n")

    for i, item in enumerate(items, 1):
        print(f"{i}. {item['name']}")
        print(f"   Modified: {item['modified']}")
        print(f"   Preview: {item['preview'][:100]}...")
        print()

    print("Use Claude Code Agent Skills to process these items:")
    print("  /inbox-processor  - Analyze and categorize items")
    print("  /task-manager     - Move items between folders")


def show_help() -> None:
    """Show help message."""
    print("FTE - Foundation Tier Workflow Automation")
    print("=" * 40)
    print("\nUsage: fte <command>\n")
    print("Commands:")
    print("  watch    Start file system watcher on Inbox folder")
    print("  status   Show current vault status")
    print("  process  List and process Inbox items")
    print("  help     Show this help message")
    print("\nAgent Skills (use with Claude Code):")
    print("  /inbox-processor   Analyze and categorize inbox items")
    print("  /task-manager      Manage task status and movement")
    print("  /dashboard-updater Refresh Dashboard.md statistics")
    print("  /note-creator      Create structured notes")


def main() -> None:
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    commands = {
        "watch": cmd_watch,
        "status": cmd_status,
        "process": cmd_process,
        "help": show_help,
        "--help": show_help,
        "-h": show_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print("Run 'fte help' for usage information.")
        sys.exit(1)


__all__ = ["VaultManager", "VaultWatcher", "watch", "main"]
