"""Action Registry - Register and execute actions for MCP server."""

import asyncio
from typing import Dict, Any, Callable, Optional, Awaitable
from pathlib import Path
import inspect
from datetime import datetime


class ActionRegistry:
    """Registry for managing and executing actions."""

    def __init__(self, vault_path: str | Path | None = None):
        """Initialize the action registry.

        Args:
            vault_path: Path to vault directory
        """
        self.actions: Dict[str, Dict[str, Any]] = {}
        self.vault_path = vault_path
        self.execution_log: list = []

    def register_action(
        self,
        name: str,
        func: Callable,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None
    ):
        """Register an action with the server.

        Args:
            name: Name of the action
            func: Function to execute
            description: Description of the action
            parameters: Parameter schema for the action
        """
        self.actions[name] = {
            "function": func,
            "description": description,
            "parameters": parameters or {},
            "registered_at": datetime.now().isoformat(),
        }

    def unregister_action(self, name: str) -> bool:
        """Remove an action from the registry.

        Args:
            name: Name of the action to remove

        Returns:
            True if action was removed, False if not found
        """
        if name in self.actions:
            del self.actions[name]
            return True
        return False

    def list_actions(self) -> list:
        """List all registered actions.

        Returns:
            List of action names
        """
        return list(self.actions.keys())

    def get_action_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific action.

        Args:
            name: Name of the action

        Returns:
            Action information or None if not found
        """
        if name in self.actions:
            action = self.actions[name]
            return {
                "name": name,
                "description": action["description"],
                "parameters": action["parameters"],
                "registered_at": action["registered_at"],
            }
        return None

    def execute_action(self, name: str, **kwargs) -> Any:
        """Execute a registered action synchronously.

        Args:
            name: Name of the action to execute
            **kwargs: Arguments to pass to the action

        Returns:
            Result of the action execution

        Raises:
            KeyError: If action is not registered
            Exception: If action execution fails
        """
        if name not in self.actions:
            raise KeyError(f"Action '{name}' not registered")

        func = self.actions[name]["function"]

        # Log execution
        log_entry = {
            "action": name,
            "arguments": kwargs,
            "executed_at": datetime.now().isoformat(),
            "sync": True,
        }
        self.execution_log.append(log_entry)

        try:
            result = func(**kwargs)
            log_entry["result"] = result
            log_entry["status"] = "success"
            return result
        except Exception as e:
            log_entry["error"] = str(e)
            log_entry["status"] = "error"
            raise

    async def execute_action_async(self, name: str, **kwargs) -> Any:
        """Execute a registered action asynchronously.

        Args:
            name: Name of the action to execute
            **kwargs: Arguments to pass to the action

        Returns:
            Result of the action execution

        Raises:
            KeyError: If action is not registered
            Exception: If action execution fails
        """
        if name not in self.actions:
            raise KeyError(f"Action '{name}' not registered")

        func = self.actions[name]["function"]

        # Log execution
        log_entry = {
            "action": name,
            "arguments": kwargs,
            "executed_at": datetime.now().isoformat(),
            "sync": False,
        }
        self.execution_log.append(log_entry)

        try:
            # Check if function is async
            if asyncio.iscoroutinefunction(func):
                result = await func(**kwargs)
            else:
                # If not async, run in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: func(**kwargs)
                )

            log_entry["result"] = result
            log_entry["status"] = "success"
            return result
        except Exception as e:
            log_entry["error"] = str(e)
            log_entry["status"] = "error"
            raise

    def validate_action_params(self, name: str, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate parameters for an action.

        Args:
            name: Name of the action
            **kwargs: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if name not in self.actions:
            return False, f"Action '{name}' not registered"

        expected_params = self.actions[name]["parameters"]

        if not expected_params:
            return True, None

        properties = expected_params.get("properties", {})
        required = expected_params.get("required", [])

        # Check required parameters
        for param in required:
            if param not in kwargs:
                return False, f"Missing required parameter: {param}"

        # Validate parameter types if specified
        for param, value in kwargs.items():
            if param in properties:
                param_schema = properties[param]
                expected_type = param_schema.get("type")

                if expected_type:
                    if expected_type == "string" and not isinstance(value, str):
                        return False, f"Parameter '{param}' must be a string"
                    elif expected_type == "integer" and not isinstance(value, int):
                        return False, f"Parameter '{param}' must be an integer"
                    elif expected_type == "number" and not isinstance(value, (int, float)):
                        return False, f"Parameter '{param}' must be a number"
                    elif expected_type == "boolean" and not isinstance(value, bool):
                        return False, f"Parameter '{param}' must be a boolean"
                    elif expected_type == "array" and not isinstance(value, list):
                        return False, f"Parameter '{param}' must be an array"

        return True, None

    def get_execution_log(self, limit: int = 100) -> list:
        """Get execution log entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of execution log entries
        """
        return self.execution_log[-limit:]

    def clear_execution_log(self):
        """Clear the execution log."""
        self.execution_log.clear()


def create_default_action_registry(vault_path: str | Path | None = None) -> ActionRegistry:
    """Create an action registry with default actions.

    Args:
        vault_path: Path to vault directory

    Returns:
        Configured ActionRegistry instance
    """
    registry = ActionRegistry(vault_path=vault_path)

    # Register default actions

    async def send_email(to: str, subject: str, body: str, vault_path: str | Path | None = None):
        """Default action to send an email."""
        # This would integrate with the existing Gmail functionality
        from ..gmail_watcher import GmailWatcher

        # In a real implementation, this would send an actual email
        # For now, just log the intent
        result = {
            "sent": False,
            "to": to,
            "subject": subject,
            "body_preview": body[:100] + "..." if len(body) > 100 else body,
            "message": "Email action received - would send in real implementation"
        }

        # In a real implementation, you'd use the Gmail API to send the email
        return result

    async def create_note(title: str, content: str, folder: str = "Inbox", vault_path: str | Path | None = None):
        """Default action to create a note in the vault."""
        from ..vault_manager import VaultManager

        manager = VaultManager(vault_path)
        file_path = manager.create_note(title=title, content=content, folder=folder)

        return {
            "success": True,
            "file_path": str(file_path),
            "title": title,
            "folder": folder
        }

    async def move_task(file_name: str, destination: str, vault_path: str | Path | None = None):
        """Default action to move a task between folders."""
        from ..skills.task_manager import move_task as move_task_skill

        result = move_task_skill(file_name, destination, vault_path)
        return result

    # Register the default actions
    registry.register_action(
        "send_email",
        send_email,
        "Send an email using Gmail API",
        {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body content"}
            },
            "required": ["to", "subject", "body"]
        }
    )

    registry.register_action(
        "create_note",
        create_note,
        "Create a new note in the vault",
        {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Note title"},
                "content": {"type": "string", "description": "Note content"},
                "folder": {"type": "string", "description": "Target folder (Inbox, Needs_Action, Done)", "default": "Inbox"}
            },
            "required": ["title", "content"]
        }
    )

    registry.register_action(
        "move_task",
        move_task,
        "Move a task file between vault folders",
        {
            "type": "object",
            "properties": {
                "file_name": {"type": "string", "description": "Name of the file to move"},
                "destination": {"type": "string", "description": "Destination folder (Inbox, Needs_Action, Done)"}
            },
            "required": ["file_name", "destination"]
        }
    )

    return registry