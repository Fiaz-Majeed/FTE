#!/usr/bin/env python3
"""
Advanced WhatsApp sender using the MCP Server integration from Silver Tier.
This script demonstrates how to send WhatsApp messages through your MCP server.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from src.fte.mcp.whatsapp_mcp_server import WhatsAppMCPServer


async def setup_and_send_whatsapp_message(to_number, message_body, account_sid=None, auth_token=None):
    """
    Setup WhatsApp integration and send a message using the MCP server.

    Args:
        to_number (str): Recipient's phone number in international format (+1234567890)
        message_body (str): Message content to send
        account_sid (str): Twilio Account SID (optional if set as env var)
        auth_token (str): Twilio Auth Token (optional if set as env var)

    Returns:
        dict: Response from the MCP server
    """

    # Get credentials from parameters or environment variables
    account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        print("Error: Twilio credentials not provided!")
        print("Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables")
        print("Or provide them as function parameters")
        return {
            'status': 'error',
            'message': 'Twilio credentials not provided'
        }

    # Create MCP server instance
    server = WhatsAppMCPServer()

    # Setup WhatsApp integration
    setup_params = {
        'account_sid': account_sid,
        'auth_token': auth_token,
        'from_number': 'whatsapp:+14155238886'  # Default Twilio WhatsApp Sandbox number
    }

    print("🔧 Setting up WhatsApp integration...")
    setup_result = await server.setup_whatsapp_integration(setup_params)

    if setup_result['status'] != 'success':
        print(f"❌ Setup failed: {setup_result['message']}")
        return setup_result

    print("✅ WhatsApp integration setup successful!")

    # Prepare message parameters
    message_params = {
        'to_number': to_number,
        'message_body': message_body
    }

    print(f"📤 Sending message to {to_number}...")
    print(f"Message: {message_body}")

    # Send the WhatsApp message
    send_result = await server.send_whatsapp_message(message_params)

    return send_result


def main():
    print("Silver Tier MCP - WhatsApp Message Sender")
    print("="*50)

    # Check if required libraries are available
    try:
        from twilio.rest import Client
        print("✅ Twilio library available")
    except ImportError:
        print("❌ Error: Twilio library not installed!")
        print("Please install it with: pip install twilio")
        return

    try:
        # Test importing the MCP server
        from src.fte.mcp.whatsapp_mcp_server import WhatsAppMCPServer
        print("✅ MCP Server available")
    except ImportError as e:
        print(f"❌ Error importing MCP server: {e}")
        return

    print("\n📝 Instructions:")
    print("1. You need a Twilio account with WhatsApp Sandbox enabled")
    print("2. Your phone number must be registered in the WhatsApp Sandbox")
    print("3. Set your Twilio credentials as environment variables")
    print("4. Use international format for phone number (+1234567890)")

    # Get recipient number
    print("\n📱 Enter your phone number (international format, e.g., +1234567890):")
    phone_number = input().strip()

    if not phone_number:
        print("❌ Phone number is required!")
        return

    if not phone_number.startswith('+'):
        print("❌ Please use international format (start with + followed by country code)")
        return

    # Get message
    print("\n💬 Enter your message:")
    message = input().strip()

    if not message:
        print("❌ Message content is required!")
        return

    print(f"\n🚀 Sending WhatsApp message via MCP Server...")

    # Run the async function
    result = asyncio.run(setup_and_send_whatsapp_message(phone_number, message))

    if result['status'] == 'success':
        print(f"\n🎉 WhatsApp message sent successfully!")
        print(f"Message SID: {result.get('message_sid', 'N/A')}")
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Timestamp: {result.get('timestamp', 'N/A')}")
    else:
        print(f"\n💥 Failed to send WhatsApp message: {result.get('message', 'Unknown error')}")
        print("\n💡 Troubleshooting tips:")
        print("  - Verify your Twilio credentials are correct")
        print("  - Ensure your phone number is registered in WhatsApp Sandbox")
        print("  - Check that your message doesn't exceed character limits")
        print("  - Confirm your Twilio account has sufficient balance")


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add the src directory to Python path to import modules
    sys.path.insert(0, str(Path(__file__).parent))

    main()