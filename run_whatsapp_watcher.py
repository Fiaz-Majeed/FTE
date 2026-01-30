#!/usr/bin/env python3
"""Script to run the WhatsApp watcher"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import fte modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    print("WhatsApp Message Monitor")
    print("="*50)
    print("To run the WhatsApp watcher, you need Twilio credentials:")
    print("")
    print("1. Create a Twilio account at https://www.twilio.com/")
    print("2. Get your Account SID and Auth Token")
    print("3. Purchase a WhatsApp-enabled phone number")
    print("4. Configure the sandbox or upgrade to full access")
    print("")
    print("Required credentials:")
    print("- TWILIO_ACCOUNT_SID: Your Twilio Account SID")
    print("- TWILIO_AUTH_TOKEN: Your Twilio Auth Token")
    print("- Your WhatsApp-enabled phone number")
    print("")

    # Check if Twilio is available
    try:
        from twilio.rest import Client
        print("+ Twilio library is installed")

        # Check if environment variables are set
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")

        if account_sid and auth_token:
            print("+ Twilio credentials are set in environment")

            try:
                # Try to create a client to test credentials
                client = Client(account_sid, auth_token)
                print("+ Twilio credentials appear to be valid")

                # Now try to run the WhatsApp watcher
                from fte.watchers.whatsapp_watcher import WhatsAppWatcher

                print("")
                print("Starting WhatsApp Watcher...")

                # Create the watcher instance
                watcher = WhatsAppWatcher(
                    account_sid=account_sid,
                    auth_token=auth_token
                )

                print("WhatsApp watcher initialized successfully!")
                print("Monitoring for new WhatsApp messages...")
                print("New messages will be saved to your vault/Inbox/ folder")
                print("Press Ctrl+C to stop monitoring")

                # Run the watcher
                watcher.run()

            except Exception as e:
                print(f"Error initializing WhatsApp watcher: {e}")
                print("This may be due to invalid Twilio credentials or permissions")

        else:
            print("")
            print("! Twilio credentials not found in environment variables")
            print("! Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN")
            print("")
            print("Example setup:")
            print("  set TWILIO_ACCOUNT_SID=your_account_sid_here")
            print("  set TWILIO_AUTH_TOKEN=your_auth_token_here")
            print("")
            print("Note: You need a Twilio account with WhatsApp Sandbox access")

    except ImportError:
        print("- Twilio library not installed")
        print("  Install with: pip install twilio")
        print("  Then set up your Twilio account and credentials")

if __name__ == "__main__":
    main()