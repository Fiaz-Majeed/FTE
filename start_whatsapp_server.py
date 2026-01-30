#!/usr/bin/env python3
"""
Script to start the WhatsApp-enabled MCP server.
"""

import sys
from pathlib import Path

def main():
    print("WhatsApp-Enabled MCP Server")
    print("="*50)

    # Check if required libraries are available
    py_mcp_available = False
    twilio_available = False

    try:
        import py_mcp
        py_mcp_available = True
        print("✓ py_mcp library is available")
    except ImportError:
        print("⚠ py_mcp library not installed - install with: pip install py_mcp")

    try:
        import twilio
        twilio_available = True
        print("✓ Twilio library is available")
    except ImportError:
        print("⚠ Twilio library not installed - install with: pip install twilio")

    print("\nTo send WhatsApp messages, you need:")
    print("1. A Twilio account with WhatsApp Sandbox enabled")
    print("2. Your Account SID and Auth Token from Twilio Console")
    print("3. Set environment variables:")
    print("   - TWILIO_ACCOUNT_SID: Your Twilio Account SID")
    print("   - TWILIO_AUTH_TOKEN: Your Twilio Auth Token")
    print("\nExample setup:")
    print("   set TWILIO_ACCOUNT_SID=your_account_sid_here")
    print("   set TWILIO_AUTH_TOKEN=your_auth_token_here")
    print("\nOnce credentials are set, you can use the MCP server to send WhatsApp messages.")

    if py_mcp_available and twilio_available:
        print("\nBoth required libraries are available!")
        print("You can now run the WhatsApp MCP server.")

        # Try to import and start the server
        try:
            from src.fte.mcp.whatsapp_mcp_server import WhatsAppMCPServer
            print("✓ WhatsAppMCPServer module loaded successfully")

            print("\nTo start the server, run:")
            print("   python -c \"from src.fte.mcp.whatsapp_mcp_server import WhatsAppMCPServer; import asyncio; server = WhatsAppMCPServer(); asyncio.run(server.start())\"")
        except ImportError as e:
            print(f"Could not import WhatsAppMCPServer: {e}")
    else:
        print("\nPlease install required libraries before starting the server:")
        print("   pip install py_mcp twilio")

if __name__ == "__main__":
    main()