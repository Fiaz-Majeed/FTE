#!/usr/bin/env python3
"""
Script to run the WhatsApp-enabled MCP server.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import fte modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    print("WhatsApp-Enabled MCP Server")
    print("="*50)

    try:
        from fte.mcp.whatsapp_mcp_server import WhatsAppMCPServer

        print("WhatsApp MCP Server module loaded successfully!")
        print("\nTo run the server, you need Twilio credentials:")
        print("- TWILIO_ACCOUNT_SID: Your Twilio Account SID")
        print("- TWILIO_AUTH_TOKEN: Your Twilio Auth Token")
        print("- Optionally: Your WhatsApp-enabled phone number")
        print("\nExample setup:")
        print("  export TWILIO_ACCOUNT_SID='your_account_sid_here'")
        print("  export TWILIO_AUTH_TOKEN='your_auth_token_here'")
        print("\nThe server will run on localhost:8000 by default.")
        print("Once credentials are set, you can send WhatsApp messages via MCP protocol.")

        # Check if py_mcp is available
        try:
            import py_mcp
            print("\n✓ py_mcp is available")
        except ImportError:
            print("\n⚠ py_mcp is not available - server will run in mock mode")

        # Check if twilio is available
        try:
            import twilio
            print("✓ Twilio library is available")
        except ImportError:
            print("⚠ Twilio library not installed - install with: pip install twilio")

        print(f"\nWhatsApp MCP Server is ready to be started.")
        print("Credentials can be provided dynamically via MCP commands.")

    except ImportError as e:
        print(f"Error importing WhatsApp MCP Server: {e}")
        print("Make sure all dependencies are installed.")

if __name__ == "__main__":
    main()