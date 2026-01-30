#!/usr/bin/env python3
"""
Guide for setting up and running the WhatsApp-enabled MCP server.
"""

def main():
    print("WhatsApp-Enabled MCP Server Setup Guide")
    print("="*50)

    print("\nTo send WhatsApp messages from this system, you have two options:")

    print("\nOPTION 1: Using the MCP Server (Advanced)")
    print("-" * 40)
    print("The system includes an MCP server with WhatsApp capabilities:")
    print("1. Requires py_mcp library: pip install py_mcp")
    print("2. Requires Twilio library: pip install twilio")
    print("3. Need Twilio account with WhatsApp Sandbox enabled")
    print("4. Commands available through MCP protocol:")
    print("   - whatsapp_send_message: Send individual messages")
    print("   - whatsapp_send_bulk: Send to multiple recipients")
    print("   - whatsapp_setup: Configure Twilio credentials")
    print("   - whatsapp_schedule_message: Schedule future messages")

    print("\nOPTION 2: Direct Python Script (Simple)")
    print("-" * 40)
    print("For immediate WhatsApp messaging, use this simple script:")

    simple_script = '''
import os
from twilio.rest import Client

def send_whatsapp(to_number, message_body):
    """Send a WhatsApp message using Twilio."""
    # Get credentials from environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        print("Error: Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN")
        return False

    try:
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=message_body,
            from_='whatsapp:+14155238886',  # Twilio Sandbox number
            to=f'whatsapp:{to_number}'
        )

        print(f"Message sent! SID: {message.sid}")
        return True

    except Exception as e:
        print(f"Error sending message: {e}")
        return False

# Example usage:
# send_whatsapp("+1234567890", "Hello from FTE system!")
'''

    print(simple_script)

    print("\nREQUIRED SETUP:")
    print("-" * 15)
    print("1. Create Twilio account at: https://www.twilio.com/")
    print("2. Enable WhatsApp Sandbox in your Twilio console")
    print("3. Get Account SID and Auth Token")
    print("4. Use the sandbox number (+14155238886) or purchase a WhatsApp-enabled number")
    print("5. Register your phone number in the WhatsApp sandbox")

    print("\nENVIRONMENT VARIABLES TO SET:")
    print("-" * 30)
    print("TWILIO_ACCOUNT_SID=your_account_sid_here")
    print("TWILIO_AUTH_TOKEN=your_auth_token_here")

    print("\nNOTE: Twilio charges apply for WhatsApp messages.")
    print("For production use, you'll need to apply for WhatsApp Business API access.")

if __name__ == "__main__":
    main()