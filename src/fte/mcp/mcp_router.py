"""
MCP Server Registry and Router
Manages multiple specialized MCP servers
"""
from typing import Dict, List, Optional, Any
from enum import Enum
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ..audit.audit_logger import get_audit_logger, AuditEventType


class MCPServerType(Enum):
    """Types of MCP servers."""
    SOCIAL = "social"
    ACCOUNTING = "accounting"
    COMMUNICATION = "communication"
    ANALYTICS = "analytics"
    GENERAL = "general"


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""
    name: str
    type: MCPServerType
    host: str
    port: int
    base_path: str = ""
    api_key: Optional[str] = None
    enabled: bool = True


class MCPServerRegistry:
    """Registry for managing multiple MCP servers."""

    def __init__(self):
        """Initialize MCP server registry."""
        self.servers: Dict[str, MCPServerConfig] = {}
        self.audit_logger = get_audit_logger()

    def register_server(self, config: MCPServerConfig):
        """Register an MCP server.

        Args:
            config: Server configuration
        """
        self.servers[config.name] = config
        self.audit_logger.log_action(
            action="register_mcp_server",
            actor="mcp_registry",
            resource=config.name,
            status="success",
            server_type=config.type.value,
            host=config.host,
            port=config.port
        )

    def unregister_server(self, name: str):
        """Unregister an MCP server.

        Args:
            name: Server name
        """
        if name in self.servers:
            del self.servers[name]
            self.audit_logger.log_action(
                action="unregister_mcp_server",
                actor="mcp_registry",
                resource=name,
                status="success"
            )

    def get_server(self, name: str) -> Optional[MCPServerConfig]:
        """Get server configuration by name.

        Args:
            name: Server name

        Returns:
            Server configuration or None
        """
        return self.servers.get(name)

    def get_servers_by_type(self, server_type: MCPServerType) -> List[MCPServerConfig]:
        """Get all servers of a specific type.

        Args:
            server_type: Server type

        Returns:
            List of server configurations
        """
        return [
            server for server in self.servers.values()
            if server.type == server_type and server.enabled
        ]

    def list_servers(self) -> List[Dict[str, Any]]:
        """List all registered servers.

        Returns:
            List of server information
        """
        return [
            {
                "name": server.name,
                "type": server.type.value,
                "host": server.host,
                "port": server.port,
                "enabled": server.enabled,
                "url": f"http://{server.host}:{server.port}{server.base_path}"
            }
            for server in self.servers.values()
        ]


class MCPRouter:
    """Router for directing requests to appropriate MCP servers."""

    def __init__(self, registry: MCPServerRegistry):
        """Initialize MCP router.

        Args:
            registry: Server registry
        """
        self.registry = registry
        self.audit_logger = get_audit_logger()

    async def route_request(
        self,
        server_name: str,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route a request to the appropriate MCP server.

        Args:
            server_name: Target server name
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            params: Query parameters

        Returns:
            Response data
        """
        server = self.registry.get_server(server_name)
        if not server:
            raise ValueError(f"Server '{server_name}' not found")

        if not server.enabled:
            raise ValueError(f"Server '{server_name}' is disabled")

        url = f"http://{server.host}:{server.port}{server.base_path}{endpoint}"

        headers = {}
        if server.api_key:
            headers["api-key"] = server.api_key

        try:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(url, params=params, headers=headers)
                elif method == "POST":
                    response = await client.post(url, json=data, params=params, headers=headers)
                elif method == "PUT":
                    response = await client.put(url, json=data, params=params, headers=headers)
                elif method == "DELETE":
                    response = await client.delete(url, params=params, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()

                self.audit_logger.log_api_call(
                    service=server_name,
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status_code,
                    actor="mcp_router"
                )

                return response.json()

        except Exception as e:
            self.audit_logger.log_error(
                f"MCP request failed: {e}",
                actor="mcp_router",
                resource=server_name,
                endpoint=endpoint
            )
            raise


# FastAPI app for MCP router
app = FastAPI(title="MCP Router", version="1.0.0")

# Global registry and router
_registry = MCPServerRegistry()
_router = MCPRouter(_registry)


def setup_default_servers():
    """Set up default MCP servers."""
    # Social media MCP server
    _registry.register_server(MCPServerConfig(
        name="social-mcp",
        type=MCPServerType.SOCIAL,
        host="localhost",
        port=8002,
        base_path="/social"
    ))

    # Accounting MCP server (Odoo)
    _registry.register_server(MCPServerConfig(
        name="accounting-mcp",
        type=MCPServerType.ACCOUNTING,
        host="localhost",
        port=8001,
        base_path="/accounting"
    ))

    # Communication MCP server
    _registry.register_server(MCPServerConfig(
        name="communication-mcp",
        type=MCPServerType.COMMUNICATION,
        host="localhost",
        port=8003,
        base_path="/communication"
    ))

    # Analytics MCP server
    _registry.register_server(MCPServerConfig(
        name="analytics-mcp",
        type=MCPServerType.ANALYTICS,
        host="localhost",
        port=8004,
        base_path="/analytics"
    ))


@app.on_event("startup")
async def startup_event():
    """Initialize servers on startup."""
    setup_default_servers()


@app.get("/servers")
async def list_servers():
    """List all registered MCP servers."""
    return {"servers": _registry.list_servers()}


@app.post("/route/{server_name}")
async def route_request(
    server_name: str,
    endpoint: str,
    method: str = "POST",
    data: Optional[Dict[str, Any]] = None
):
    """Route a request to a specific MCP server."""
    try:
        result = await _router.route_request(server_name, endpoint, method, data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "servers_registered": len(_registry.servers),
        "servers_enabled": len([s for s in _registry.servers.values() if s.enabled])
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
