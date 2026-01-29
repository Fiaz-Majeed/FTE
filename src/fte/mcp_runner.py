"""MCP Server Runner - Main entry point for the MCP server."""

import argparse
import sys
from pathlib import Path

# Add the src directory to the path so we can import fte modules
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from .mcp.server import create_default_mcp_server


def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="FTE MCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--vault-path", help="Path to vault directory")

    args = parser.parse_args()

    # Create and run the server
    server = create_default_mcp_server(vault_path=args.vault_path)

    print(f"MCP Server starting...")
    print(f"API Key: {server.get_api_key()}")
    print("Press Ctrl+C to stop...")

    server.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()