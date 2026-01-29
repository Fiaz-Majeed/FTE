"""FTE - Foundation Tier workflow automation with Obsidian vault integration."""

import sys
from pathlib import Path

from .vault_manager import VaultManager
from .watcher import VaultWatcher, watch
from .gmail_watcher import GmailWatcher, watch as gmail_watch
from .watchers.whatsapp_watcher import WhatsAppWatcher, watch as whatsapp_watch
from .watchers.linkedin_watcher import LinkedInWatcher, watch as linkedin_watch
from .watchers.enhanced_file_watcher import EnhancedVaultWatcher, watch as enhanced_watch


def cmd_watch() -> None:
    """Start the file system watcher."""
    print("FTE Vault Watcher")
    print("=" * 40)
    watch()


def cmd_gmail() -> None:
    """Start the Gmail watcher."""
    print("FTE Gmail Watcher")
    print("=" * 40)
    gmail_watch()


def cmd_whatsapp() -> None:
    """Start the WhatsApp watcher."""
    print("FTE WhatsApp Watcher")
    print("=" * 40)
    try:
        from .watchers.whatsapp_watcher import watch as whatsapp_watch
        whatsapp_watch()
    except ImportError as e:
        print(f"WhatsApp watcher not available: {e}")
        print("Install Twilio: pip install twilio")


def cmd_linkedin() -> None:
    """Start the LinkedIn watcher."""
    print("FTE LinkedIn Watcher")
    print("=" * 40)
    try:
        from .watchers.linkedin_watcher import watch as linkedin_watch
        linkedin_watch()
    except ImportError as e:
        print(f"LinkedIn watcher not available: {e}")
        print("Install linkedin-api: pip install linkedin-api")


def cmd_enhanced_watch() -> None:
    """Start the enhanced file system watcher."""
    print("FTE Enhanced File Watcher")
    print("=" * 40)
    try:
        from .watchers.enhanced_file_watcher import watch as enhanced_watch
        enhanced_watch()
    except ImportError as e:
        print(f"Enhanced watcher not available: {e}")


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
    print("  watch          Start file system watcher on Inbox folder")
    print("  gmail          Start Gmail watcher for new emails")
    print("  whatsapp       Start WhatsApp watcher for new messages")
    print("  linkedin       Start LinkedIn watcher for notifications/messages")
    print("  enhanced-watch Start enhanced file system watcher")
    print("  status         Show current vault status")
    print("  process        List and process Inbox items")
    print("  help           Show this help message")
    print("\nAgent Skills (use with Claude Code):")
    print("  /inbox-processor   Analyze and categorize inbox items")
    print("  /task-manager      Manage task status and movement")
    print("  /dashboard-updater Refresh Dashboard.md statistics")
    print("  /note-creator      Create structured notes")
    print("  /plan-reasoning    Process Plan.md files with Claude reasoning")
    print("  /linkedin-posting  Automate LinkedIn posts about business")
    print("  /approval-workflow Handle human-in-the-loop approval for actions")
    print("  /scheduler-skills  Schedule and manage recurring tasks")


def main() -> None:
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    commands = {
        "watch": cmd_watch,
        "gmail": cmd_gmail,
        "whatsapp": cmd_whatsapp,
        "linkedin": cmd_linkedin,
        "enhanced-watch": cmd_enhanced_watch,
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


__all__ = ["VaultManager", "VaultWatcher", "GmailWatcher", "watch", "gmail_watch", "main"]
