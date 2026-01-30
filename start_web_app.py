#!/usr/bin/env python3
"""
Script to start the WhatsApp Web Application
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import flask
        import twilio
        return True
    except ImportError:
        return False

def install_requirements():
    """Install required packages from requirements.txt."""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    print("WhatsApp Web Application - Silver Tier")
    print("="*40)

    # Check if templates directory exists
    templates_dir = Path("templates")
    if not templates_dir.exists():
        templates_dir.mkdir(exist_ok=True)
        print("Created templates directory")

    # Check if required packages are installed
    if not check_requirements():
        print("Required packages not found.")
        install_choice = input("Do you want to install them now? (y/n): ").strip().lower()

        if install_choice in ['y', 'yes']:
            try:
                install_requirements()
                print("Packages installed successfully!")
            except Exception as e:
                print(f"Error installing packages: {e}")
                return
        else:
            print("Please install required packages manually using: pip install -r requirements.txt")
            return

    # Check for environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        print("\n⚠️  Warning: Twilio credentials not found in environment variables!")
        print("Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN before continuing.")
        print("\nOn Windows:")
        print("set TWILIO_ACCOUNT_SID=your_account_sid")
        print("set TWILIO_AUTH_TOKEN=your_auth_token")
        print("\nOn Linux/Mac:")
        print("export TWILIO_ACCOUNT_SID=your_account_sid")
        print("export TWILIO_AUTH_TOKEN=your_auth_token")
        return

    print(f"\n✅ Credentials found: {bool(account_sid) and bool(auth_token)}")
    print("\nThe web application will start on http://localhost:5000")
    print("You can access this from any device on the same network using the IP address.")
    print("\nPress Ctrl+C to stop the server.\n")

    # Ask if user wants to open the browser
    open_browser = input("Open the application in your browser? (y/n): ").strip().lower()

    try:
        # Import the Flask app
        from web_whatsapp_app import app

        # Open browser if requested
        if open_browser in ['y', 'yes']:
            import threading
            import time

            def open_browser_when_ready():
                time.sleep(2)  # Wait a bit for server to start
                webbrowser.open("http://localhost:5000")

            browser_thread = threading.Thread(target=open_browser_when_ready)
            browser_thread.daemon = True
            browser_thread.start()

        # Start the Flask app
        app.run(debug=False, host='0.0.0.0', port=5000)

    except KeyboardInterrupt:
        print("\n\nApplication stopped by user.")
    except Exception as e:
        print(f"\nError starting application: {e}")

if __name__ == "__main__":
    main()