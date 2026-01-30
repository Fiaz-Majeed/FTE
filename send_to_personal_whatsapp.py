#!/usr/bin/env python3
"""
Script to send WhatsApp messages from the Silver Tier system to your personal WhatsApp.
This script uses the existing Twilio integration in your system.
"""

import os
from twilio.rest import Client


def send_whatsapp_to_personal(number, message):
    """
    Send a WhatsApp message to your personal number using Twilio.

    Args:
        number (str): Your phone number in international format (e.g., +1234567890)
        message (str): The message to send

    Returns:
        bool: True if successful, False otherwise
    """

    # Get Twilio credentials from environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        print("Error: Twilio credentials not found!")
        print("Please set the following environment variables:")
        print("  - TWILIO_ACCOUNT_SID: Your Twilio Account SID")
        print("  - TWILIO_AUTH_TOKEN: Your Twilio Auth Token")
        print("\nYou can get these from your Twilio Console after signing up.")
        return False

    # Initialize Twilio client
    client = Client(account_sid, auth_token)

    try:
        # Send WhatsApp message
        # Note: The 'from_' parameter should be your Twilio WhatsApp number
        # which is typically whatsapp:+14155238886 for the sandbox
        message_obj = client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # This is Twilio's WhatsApp Sandbox number
            to=f'whatsapp:{number}'         # Your personal number
        )

        print(f"✅ Message sent successfully!")
        print(f"Message SID: {message_obj.sid}")
        print(f"Status: {message_obj.status}")
        return True

    except Exception as e:
        print(f"❌ Error sending message: {str(e)}")
        return False


def main():
    print("Silver Tier - Send WhatsApp to Personal Number")
    print("="*50)

    # Check if Twilio is available
    try:
        from twilio.rest import Client
    except ImportError:
        print("❌ Error: Twilio library not installed!")
        print("Please install it with: pip install twilio")
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

    print(f"\n📤 Sending message to {phone_number}...")
    print(f"Message: {message}")

    success = send_whatsapp_to_personal(phone_number, message)

    if success:
        print("\n🎉 WhatsApp message sent successfully!")
    else:
        print("\n💥 Failed to send WhatsApp message.")
        print("\n💡 Troubleshooting tips:")
        print("  - Verify your Twilio credentials are correct")
        print("  - Ensure your phone number is registered in WhatsApp Sandbox")
        print("  - Check that your message doesn't exceed character limits")
        print("  - Confirm your Twilio account has sufficient balance")


if __name__ == "__main__":
    main()