"""Enhanced File System Watcher - Monitor multiple directories with pattern matching."""

import time
import re
from pathlib import Path
from datetime import datetime
from typing import Callable, List, Dict, Any, Optional
from fnmatch import fnmatch

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from ..vault_manager import VaultManager


class EnhancedInboxEventHandler(FileSystemEventHandler):
    """Handle file system events with pattern matching and multiple directories."""

    def __init__(
        self,
        callback: Callable[[str, str, Path], None] | None = None,
        patterns: List[str] | None = None,
        exclude_patterns: List[str] | None = None,
    ):
        """Initialize the event handler.

        Args:
            callback: Optional callback function(event_type, event_path, file_path)
            patterns: List of file patterns to watch (e.g., ['*.txt', '*.md'])
            exclude_patterns: List of file patterns to exclude
        """
        super().__init__()
        self.callback = callback
        self.patterns = patterns or ["*"]
        self.exclude_patterns = exclude_patterns or []

    def _matches_pattern(self, path: Path) -> bool:
        """Check if path matches inclusion/exclusion patterns.

        Args:
            path: Path to check

        Returns:
            True if path matches inclusion patterns and doesn't match exclusion patterns
        """
        path_str = str(path)

        # Check exclusion patterns first
        for pattern in self.exclude_patterns:
            if fnmatch(path_str, pattern):
                return False

        # Check inclusion patterns
        for pattern in self.patterns:
            if fnmatch(path_str, pattern):
                return True

        return False

    def _log_event(self, event_type: str, event: FileSystemEvent) -> None:
        """Log a file system event.

        Args:
            event_type: Type of event (created, modified, deleted, moved)
            event: The file system event
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        path = Path(event.src_path)

        # Check if file matches our patterns
        if not self._matches_pattern(path):
            return

        # Skip hidden files
        if path.name.startswith("."):
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


class EnhancedVaultWatcher:
    """Watch multiple vault directories for file changes with pattern matching."""

    def __init__(
        self,
        vault_paths: List[str | Path] | None = None,
        callback: Callable[[str, str, Path], None] | None = None,
        patterns: List[str] | None = None,
        exclude_patterns: List[str] | None = None,
    ):
        """Initialize the enhanced vault watcher.

        Args:
            vault_paths: List of paths to watch. Defaults to [./vault/Inbox]
            callback: Optional callback for events
            patterns: List of file patterns to watch (e.g., ['*.txt', '*.md'])
            exclude_patterns: List of file patterns to exclude
        """
        base_path = Path(__file__).parent.parent.parent

        if vault_paths is None:
            vault_paths = [base_path / "vault" / "Inbox"]

        self.vault_paths = [Path(vp) for vp in vault_paths]
        self.observer = Observer()
        self.event_handler = EnhancedInboxEventHandler(
            callback, patterns, exclude_patterns
        )
        self._running = False

    def start(self) -> None:
        """Start watching the specified directories."""
        for vault_path in self.vault_paths:
            if not vault_path.exists():
                vault_path.mkdir(parents=True, exist_ok=True)

            self.observer.schedule(
                self.event_handler,
                str(vault_path),
                recursive=True,  # Enable recursive watching
            )
            print(f"Watching: {vault_path}")

        self.observer.start()
        self._running = True

        print("Press Ctrl+C to stop...")

    def stop(self) -> None:
        """Stop watching."""
        if self._running:
            self.observer.stop()
            self.observer.join()
            self._running = False
            print("\nEnhanced watcher stopped.")

    def run(self) -> None:
        """Run the watcher until interrupted."""
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()


def watch(
    vault_paths: List[str | Path] | None = None,
    patterns: List[str] | None = None,
    exclude_patterns: List[str] | None = None,
) -> None:
    """Convenience function to start watching.

    Args:
        vault_paths: List of paths to watch
        patterns: List of file patterns to watch
        exclude_patterns: List of file patterns to exclude
    """
    watcher = EnhancedVaultWatcher(
        vault_paths=vault_paths,
        patterns=patterns,
        exclude_patterns=exclude_patterns,
    )
    watcher.run()


if __name__ == "__main__":
    watch()