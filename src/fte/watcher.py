"""File System Watcher - Monitor the vault Inbox for changes."""

import time
from pathlib import Path
from datetime import datetime
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class InboxEventHandler(FileSystemEventHandler):
    """Handle file system events in the Inbox folder."""

    def __init__(self, callback: Callable[[str, str, Path], None] | None = None):
        """Initialize the event handler.

        Args:
            callback: Optional callback function(event_type, event_path, file_path)
        """
        super().__init__()
        self.callback = callback

    def _log_event(self, event_type: str, event: FileSystemEvent) -> None:
        """Log a file system event.

        Args:
            event_type: Type of event (created, modified, deleted, moved)
            event: The file system event
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        path = Path(event.src_path)

        # Skip non-markdown files and hidden files
        if path.name.startswith("."):
            return
        if path.suffix != ".md" and not event.is_directory:
            return

        print(f"[{timestamp}] {event_type.upper()}: {path.name}")

        if self.callback:
            self.callback(event_type, str(event.src_path), path)

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if not event.is_directory:
            self._log_event("created", event)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory:
            self._log_event("modified", event)

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events."""
        if not event.is_directory:
            self._log_event("deleted", event)

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move events."""
        if not event.is_directory:
            self._log_event("moved", event)


class VaultWatcher:
    """Watch the vault Inbox folder for file changes."""

    def __init__(
        self,
        vault_path: str | Path | None = None,
        callback: Callable[[str, str, Path], None] | None = None,
    ):
        """Initialize the vault watcher.

        Args:
            vault_path: Path to the vault directory. Defaults to ./vault
            callback: Optional callback for events
        """
        if vault_path is None:
            vault_path = Path(__file__).parent.parent.parent / "vault"
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.observer = Observer()
        self.event_handler = InboxEventHandler(callback)
        self._running = False

    def start(self) -> None:
        """Start watching the Inbox folder."""
        if not self.inbox_path.exists():
            self.inbox_path.mkdir(parents=True, exist_ok=True)

        self.observer.schedule(
            self.event_handler,
            str(self.inbox_path),
            recursive=False,
        )
        self.observer.start()
        self._running = True

        print(f"Watching: {self.inbox_path}")
        print("Press Ctrl+C to stop...")

    def stop(self) -> None:
        """Stop watching."""
        if self._running:
            self.observer.stop()
            self.observer.join()
            self._running = False
            print("\nWatcher stopped.")

    def run(self) -> None:
        """Run the watcher until interrupted."""
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()


def watch(vault_path: str | Path | None = None) -> None:
    """Convenience function to start watching.

    Args:
        vault_path: Path to the vault directory
    """
    watcher = VaultWatcher(vault_path)
    watcher.run()


if __name__ == "__main__":
    watch()
