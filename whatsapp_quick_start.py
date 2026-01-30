#!/usr/bin/env python3
"""
Simple example of sending WhatsApp messages from Silver Tier to your personal device.
This script demonstrates the integration points available in your system.
"""

import os
import asyncio
from twilio.rest import Client

def send_whatsapp_example():
    """
    Example function showing how to send WhatsApp messages.
    Replace with your actual credentials and phone number.
    """

    # Get credentials from environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        print("[ERROR] Twilio credentials not found!")
        print("Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.")
        return False

    # Initialize Twilio client
    client = Client(account_sid, auth_token)

    # Example: Send a message to your personal WhatsApp
    # Replace '+1234567890' with your actual phone number in international format
    to_number = input("Enter your phone number in international format (e.g., +1234567890): ").strip()

    if not to_number.startswith('+'):
        print("[ERROR] Please use international format (start with + followed by country code)")
        return False

    message_body = input("Enter your message: ").strip()

    if not message_body:
        print("[ERROR] Message content is required!")
        return False

    try:
        # Send WhatsApp message using Twilio
        message = client.messages.create(
            body=message_body,
            from_='whatsapp:+14155238886',  # Twilio's WhatsApp Sandbox number
            to=f'whatsapp:{to_number}'
        )

        print(f"[SUCCESS] Message sent successfully!")
        print(f"SID: {message.sid}")
        print(f"Status: {message.status}")
        print(f"To: {to_number}")
        print(f"Message: {message_body}")

        return True

    except Exception as e:
        print(f"[ERROR] Error sending message: {str(e)}")
        return False

def main():
    print("Silver Tier WhatsApp Integration - Quick Start")
    print("="*50)
    print()
    print("This script demonstrates how to send WhatsApp messages from your")
    print("Silver Tier system to your personal WhatsApp device.")
    print()
    print("Requirements:")
    print("1. Twilio account with WhatsApp Sandbox enabled")
    print("2. Your phone number registered in the WhatsApp Sandbox")
    print("3. Environment variables set (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)")
    print()

    # Check if Twilio is available
    try:
        from twilio.rest import Client
    except ImportError:
        print("❌ Twilio library not installed!")
        print("Install with: pip install twilio")
        return

    print("[OK] Twilio library is available")

    # Show current status
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if account_sid and auth_token:
        print("[OK] Twilio credentials are set")
        print()

        # Proceed with sending
        success = send_whatsapp_example()

        if success:
            print()
            print("[SUCCESS] WhatsApp message sent successfully!")
            print()
            print("💡 Pro tip: You can integrate this functionality into your")
            print("   automated workflows by calling the send_whatsapp_message")
            print("   function from your business logic.")
        else:
            print()
            print("[FAILURE] Failed to send WhatsApp message.")

    else:
        print("[ERROR] Twilio credentials not set!")
        print()
        print("To set up your credentials:")
        print("1. Create a Twilio account at https://www.twilio.com/")
        print("2. Enable WhatsApp Sandbox in your Twilio console")
        print("3. Get your Account SID and Auth Token")
        print("4. Set environment variables:")
        print("   Windows: set TWILIO_ACCOUNT_SID=your_sid")
        print("            set TWILIO_AUTH_TOKEN=your_token")
        print("   Linux/Mac: export TWILIO_ACCOUNT_SID=your_sid")
        print("              export TWILIO_AUTH_TOKEN=your_token")
        print()
        print("5. Register your phone number in WhatsApp Sandbox by sending")
        print("   'join <keyword>' to the sandbox number provided by Twilio")

if __name__ == "__main__":
    main()