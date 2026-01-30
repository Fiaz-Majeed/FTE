#!/usr/bin/env python3
"""
Direct WhatsApp sender - sends WhatsApp message with credentials provided as input.
"""

import os
from twilio.rest import Client


def send_whatsapp_direct(account_sid, auth_token, to_number, message_body):
    """
    Send a WhatsApp message directly with provided credentials.

    Args:
        account_sid (str): Twilio Account SID
        auth_token (str): Twilio Auth Token
        to_number (str): Recipient's phone number in international format
        message_body (str): Message to send

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)

        # Send WhatsApp message
        message = client.messages.create(
            body=message_body,
            from_='whatsapp:+14155238886',  # Twilio's WhatsApp Sandbox number
            to=f'whatsapp:{to_number}'
        )

        print(f"[SUCCESS] Message sent successfully!")
        print(f"SID: {message.sid}")
        print(f"Status: {message.status}")
        print(f"Timestamp: {message.date_sent}")
        return True

    except Exception as e:
        print(f"[ERROR] Error sending message: {str(e)}")
        return False


def main():
    print("Silver Tier - Direct WhatsApp Sender")
    print("="*40)
    print()
    print("This script sends a WhatsApp message using provided credentials.")
    print()

    # Get credentials from user input
    print("Enter your Twilio credentials:")
    account_sid = input("Account SID: ").strip()
    auth_token = input("Auth Token: ").strip()

    if not account_sid or not auth_token:
        print("[ERROR] Account SID and Auth Token are required!")
        return

    # Get recipient number
    to_number = input("Enter recipient phone number (e.g., +923349739727): ").strip()

    if not to_number.startswith('+'):
        print("[ERROR] Please use international format (start with + followed by country code)")
        return

    # Get message
    message_body = input("Enter your message: ").strip()

    if not message_body:
        print("[ERROR] Message content is required!")
        return

    print(f"\nSending message to {to_number}...")
    print(f"Message: {message_body}")

    success = send_whatsapp_direct(account_sid, auth_token, to_number, message_body)

    if success:
        print("\n🎉 WhatsApp message sent successfully!")
    else:
        print("\n💥 Failed to send WhatsApp message.")


if __name__ == "__main__":
    main()