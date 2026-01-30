#!/usr/bin/env python3
"""
Script to send "how are you" message to +923349739727 using the provided credentials.
"""

from twilio.rest import Client


def send_how_are_you_message():
    """
    Send "how are you" message to +923349739727 using the provided credentials.
    """
    # Get credentials from environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    # Target number and message
    to_number = "+923349739727"
    message_body = "how are you"

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
        print(f"To: {to_number}")
        print(f"Message: {message_body}")
        print(f"Timestamp: {message.date_sent}")
        return True

    except Exception as e:
        print(f"[ERROR] Error sending message: {str(e)}")
        return False


if __name__ == "__main__":
    print("Sending 'how are you' message to +923349739727...")
    success = send_how_are_you_message()

    if success:
        print("\n[SUCCESS] WhatsApp message sent successfully!")
    else:
        print("\n[ERROR] Failed to send WhatsApp message.")
        print("\nNote: Make sure that +923349739727 is registered in your Twilio WhatsApp Sandbox.")