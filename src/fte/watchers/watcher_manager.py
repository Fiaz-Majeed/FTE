"""
Consolidated Watcher Manager for the FTE automation system.
Manages all watcher processes, provides health monitoring, and status reporting.
"""
import asyncio
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from .linkedin_watcher import LinkedInWatcher
from .whatsapp_watcher import WhatsAppWatcher
from ..gmail_watcher import GmailWatcher


class WatcherStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"
    PAUSED = "paused"


@dataclass
class WatcherInfo:
    """Information about a watcher instance."""
    name: str
    status: WatcherStatus
    last_updated: datetime
    error_message: Optional[str] = None
    thread: Optional[threading.Thread] = None


class WatcherManager:
    """Centralized manager for all watcher processes."""

    def __init__(self):
        self.watchers: Dict[str, WatcherInfo] = {}
        self._stop_event = threading.Event()
        self.logger = logging.getLogger(__name__)

    def register_watcher(self, name: str, watcher_instance) -> bool:
        """Register a new watcher with the manager."""
        try:
            watcher_info = WatcherInfo(
                name=name,
                status=WatcherStatus.STOPPED,
                last_updated=datetime.now(),
                thread=None
            )

            # Store the watcher instance as an attribute for later use
            setattr(self, f"{name.lower()}_instance", watcher_instance)
            self.watchers[name] = watcher_info

            self.logger.info(f"Registered watcher: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register watcher {name}: {str(e)}")
            return False

    def start_watcher(self, name: str) -> bool:
        """Start a specific watcher."""
        if name not in self.watchers:
            self.logger.error(f"Watcher {name} not registered")
            return False

        try:
            watcher_info = self.watchers[name]
            watcher_instance = getattr(self, f"{name.lower()}_instance")

            # Create and start the thread
            thread = threading.Thread(
                target=self._run_watcher,
                args=(name, watcher_instance),
                daemon=True
            )
            thread.start()

            watcher_info.thread = thread
            watcher_info.status = WatcherStatus.RUNNING
            watcher_info.last_updated = datetime.now()

            self.logger.info(f"Started watcher: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start watcher {name}: {str(e)}")
            watcher_info.status = WatcherStatus.ERROR
            watcher_info.error_message = str(e)
            return False

    def _run_watcher(self, name: str, watcher_instance):
        """Run a watcher in a separate thread."""
        try:
            # Different watchers might have different run methods
            if hasattr(watcher_instance, 'start'):
                watcher_instance.start()
            elif hasattr(watcher_instance, 'run'):
                watcher_instance.run()
            elif callable(watcher_instance):
                watcher_instance()

        except Exception as e:
            self.logger.error(f"Watcher {name} encountered an error: {str(e)}")
            watcher_info = self.watchers[name]
            watcher_info.status = WatcherStatus.ERROR
            watcher_info.error_message = str(e)
            watcher_info.last_updated = datetime.now()

    def stop_watcher(self, name: str) -> bool:
        """Stop a specific watcher."""
        if name not in self.watchers:
            self.logger.error(f"Watcher {name} not registered")
            return False

        try:
            watcher_info = self.watchers[name]
            if watcher_info.thread and watcher_info.thread.is_alive():
                # Try to gracefully stop the watcher
                watcher_instance = getattr(self, f"{name.lower()}_instance")
                if hasattr(watcher_instance, 'stop'):
                    watcher_instance.stop()
                elif hasattr(watcher_instance, 'terminate'):
                    watcher_instance.terminate()

                # Wait for thread to finish with timeout
                watcher_info.thread.join(timeout=5.0)

                if watcher_info.thread.is_alive():
                    self.logger.warning(f"Watcher {name} did not stop gracefully")

                watcher_info.status = WatcherStatus.STOPPED
                watcher_info.last_updated = datetime.now()

                self.logger.info(f"Stopped watcher: {name}")
                return True
            else:
                self.logger.info(f"Watcher {name} is not running")
                return True
        except Exception as e:
            self.logger.error(f"Failed to stop watcher {name}: {str(e)}")
            return False

    def start_all_watchers(self) -> Dict[str, bool]:
        """Start all registered watchers."""
        results = {}
        for name in self.watchers.keys():
            results[name] = self.start_watcher(name)
        return results

    def stop_all_watchers(self) -> Dict[str, bool]:
        """Stop all registered watchers."""
        results = {}
        for name in self.watchers.keys():
            results[name] = self.stop_watcher(name)
        return results

    def get_status(self, name: str) -> Optional[WatcherInfo]:
        """Get status of a specific watcher."""
        return self.watchers.get(name)

    def get_all_statuses(self) -> Dict[str, WatcherInfo]:
        """Get status of all watchers."""
        # Update statuses based on thread states
        for name, info in self.watchers.items():
            if info.thread:
                if not info.thread.is_alive() and info.status == WatcherStatus.RUNNING:
                    info.status = WatcherStatus.STOPPED
                    info.last_updated = datetime.now()

        return self.watchers.copy()

    def health_check(self) -> Dict[str, bool]:
        """Perform health check on all watchers."""
        statuses = self.get_all_statuses()
        health_report = {}

        for name, info in statuses.items():
            health_report[name] = info.status == WatcherStatus.RUNNING

        return health_report

    def restart_watcher(self, name: str) -> bool:
        """Restart a specific watcher."""
        if self.stop_watcher(name):
            return self.start_watcher(name)
        return False

    def restart_all_watchers(self) -> Dict[str, bool]:
        """Restart all watchers."""
        results = {}
        for name in self.watchers.keys():
            results[name] = self.restart_watcher(name)
        return results

    def cleanup(self):
        """Clean up all watchers before shutdown."""
        self.stop_all_watchers()


# Global watcher manager instance
watcher_manager = WatcherManager()


def initialize_watchers():
    """Initialize and register all watchers with the manager."""
    global watcher_manager

    # Initialize individual watchers
    gmail_watcher = GmailWatcher()
    linkedin_watcher = LinkedInWatcher()
    whatsapp_watcher = WhatsAppWatcher()

    # Register watchers
    watcher_manager.register_watcher("Gmail", gmail_watcher)
    watcher_manager.register_watcher("LinkedIn", linkedin_watcher)
    watcher_manager.register_watcher("WhatsApp", whatsapp_watcher)

    return watcher_manager


if __name__ == "__main__":
    # Example usage
    manager = initialize_watchers()

    print("Starting all watchers...")
    start_results = manager.start_all_watchers()
    print(f"Start results: {start_results}")

    print("\nGetting statuses...")
    statuses = manager.get_all_statuses()
    for name, info in statuses.items():
        print(f"{name}: {info.status.value}")

    print("\nPerforming health check...")
    health = manager.health_check()
    print(f"Health report: {health}")