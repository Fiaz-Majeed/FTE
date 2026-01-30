#!/usr/bin/env python3
"""
Script to send a WhatsApp message using Twilio API.
Note: Requires Twilio account with WhatsApp Sandbox enabled.
"""

import os
from twilio.rest import Client

def send_whatsapp_message(to_number, message_body, account_sid=None, auth_token=None):
    """
    Send a WhatsApp message using Twilio API.

    Args:
        to_number (str): Recipient's phone number in format +1234567890
        message_body (str): Message content to send
        account_sid (str): Twilio Account SID (optional if set as env var)
        auth_token (str): Twilio Auth Token (optional if set as env var)

    Returns:
        bool: True if message sent successfully, False otherwise
    """

    # Get credentials from parameters or environment variables
    account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        print("Error: Twilio credentials not provided!")
        print("Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables")
        print("Or provide them as function parameters")
        return False

    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)

        # Send WhatsApp message
        # Note: Twilio WhatsApp messages must start with 'whatsapp:' prefix
        message = client.messages.create(
            body=message_body,
            from_='whatsapp:+14155238886',  # This is the Twilio WhatsApp Sandbox number
            to=f'whatsapp:{to_number}'
        )

        print(f"Message sent successfully!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        return True

    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def main():
    print("WhatsApp Message Sender")
    print("="*40)

    # Check if Twilio is available
    try:
        from twilio.rest import Client
    except ImportError:
        print("Error: Twilio library not installed!")
        print("Install it with: pip install twilio")
        return

    # Get credentials
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        print("Twilio credentials not found in environment variables.")
        print("\nTo send WhatsApp messages, you need:")
        print("1. A Twilio account with WhatsApp Sandbox enabled")
        print("2. Your Account SID and Auth Token from Twilio Console")
        print("3. Set environment variables:")
        print("   - TWILIO_ACCOUNT_SID: Your Twilio Account SID")
        print("   - TWILIO_AUTH_TOKEN: Your Twilio Auth Token")
        print("4. Your phone number must be registered in the WhatsApp Sandbox")
        print("\nExample setup:")
        print("   set TWILIO_ACCOUNT_SID=your_account_sid_here")
        print("   set TWILIO_AUTH_TOKEN=your_auth_token_here")
        return

    # Get recipient number and message
    print("\nEnter the details for your WhatsApp message:")
    to_number = input("Recipient phone number (format: +1234567890): ").strip()
    message_body = input("Message content: ").strip()

    if not to_number or not message_body:
        print("Error: Both phone number and message content are required!")
        return

    print(f"\nSending WhatsApp message to {to_number}...")
    success = send_whatsapp_message(to_number, message_body)

    if success:
        print("\n✅ WhatsApp message sent successfully!")
    else:
        print("\n❌ Failed to send WhatsApp message.")

if __name__ == "__main__":
    main()