"""MCP Server - Managed Control Plane server for external actions."""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import secrets
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

from .action_registry import ActionRegistry


class MCPServer:
    """Managed Control Plane server for handling external actions."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        vault_path: str | Path | None = None,
        api_key: str | None = None,
    ):
        """Initialize the MCP server.

        Args:
            host: Host address to bind to
            port: Port to listen on
            vault_path: Path to vault directory
            api_key: API key for authentication (auto-generated if None)
        """
        self.host = host
        self.port = port
        self.base_path = Path(__file__).parent.parent.parent
        if vault_path is None:
            self.vault_path = self.base_path / "vault"
        else:
            self.vault_path = Path(vault_path)

        # Initialize action registry
        self.action_registry = ActionRegistry(vault_path=self.vault_path)

        # Generate or set API key
        self.api_key = api_key or self._generate_api_key()

        # Initialize FastAPI app
        self.app = FastAPI(
            title="FTE MCP Server",
            description="Managed Control Plane for FTE external actions",
            version="1.0.0"
        )

        # Security
        self.security = HTTPBearer()

        # Register routes
        self._setup_routes()

    def _generate_api_key(self) -> str:
        """Generate a secure API key.

        Returns:
            Generated API key
        """
        return secrets.token_urlsafe(32)

    def _verify_api_key(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Verify API key from authorization header.

        Args:
            credentials: Authorization credentials from header

        Raises:
            HTTPException: If API key is invalid
        """
        if credentials.credentials != self.api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")

    def _setup_routes(self):
        """Setup API routes."""
        @self.app.get("/")
        async def root():
            return {
                "message": "FTE MCP Server",
                "status": "running",
                "api_key_required": True,
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "api_key_valid": True
            }

        @self.app.get("/actions", dependencies=[Depends(self._verify_api_key)])
        async def list_actions():
            """List all registered actions."""
            return {
                "actions": self.action_registry.list_actions(),
                "count": len(self.action_registry.list_actions()),
                "timestamp": datetime.now().isoformat()
            }

        @self.app.post("/actions/{action_name}/execute", dependencies=[Depends(self._verify_api_key)])
        async def execute_action(action_name: str, params: Dict[str, Any]):
            """Execute a registered action.

            Args:
                action_name: Name of the action to execute
                params: Parameters for the action

            Returns:
                Result of the action execution
            """
            try:
                result = await self.action_registry.execute_action_async(action_name, **params)
                return {
                    "action": action_name,
                    "result": result,
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.get("/actions/{action_name}", dependencies=[Depends(self._verify_api_key)])
        async def get_action_info(action_name: str):
            """Get information about a specific action.

            Args:
                action_name: Name of the action

            Returns:
                Action information
            """
            action_info = self.action_registry.get_action_info(action_name)
            if not action_info:
                raise HTTPException(status_code=404, detail="Action not found")

            return {
                "action": action_name,
                "info": action_info,
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/logs", dependencies=[Depends(self._verify_api_key)])
        async def get_logs(limit: int = 100):
            """Get server logs.

            Args:
                limit: Maximum number of log entries to return

            Returns:
                Log entries
            """
            # In a real implementation, this would read from a log file
            # For now, returning empty list
            return {
                "logs": [],
                "limit": limit,
                "timestamp": datetime.now().isoformat()
            }

    def register_action(
        self,
        name: str,
        func,
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
        self.action_registry.register_action(name, func, description, parameters)

    def get_api_key(self) -> str:
        """Get the API key for the server.

        Returns:
            API key
        """
        return self.api_key

    def run(self, host: str | None = None, port: int | None = None):
        """Run the MCP server.

        Args:
            host: Host to bind to (uses default if None)
            port: Port to listen on (uses default if None)
        """
        run_host = host or self.host
        run_port = port or self.port

        print(f"MCP Server starting on {run_host}:{run_port}")
        print(f"API Key: {self.api_key}")
        print("Press Ctrl+C to stop...")

        uvicorn.run(
            self.app,
            host=run_host,
            port=run_port,
            log_level="info"
        )


def create_default_mcp_server(vault_path: str | Path | None = None) -> MCPServer:
    """Create an MCP server with default actions.

    Args:
        vault_path: Path to vault directory

    Returns:
        Configured MCPServer instance
    """
    server = MCPServer(vault_path=vault_path)

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
    server.register_action(
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

    server.register_action(
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

    server.register_action(
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

    return server


if __name__ == "__main__":
    # Create and run the default server
    server = create_default_mcp_server()
    server.run()