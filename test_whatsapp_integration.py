#!/usr/bin/env python3
"""
Test script to verify WhatsApp integration is working properly.
"""

import os
import sys
from pathlib import Path

def test_twilio_installation():
    """Test if Twilio is properly installed."""
    try:
        from twilio.rest import Client
        print("[OK] Twilio library is installed")
        return True
    except ImportError:
        print("[ERROR] Twilio library is not installed")
        print("Install it with: pip install twilio")
        return False

def test_credentials():
    """Test if Twilio credentials are set."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if account_sid and auth_token:
        print("[OK] Twilio credentials are set in environment variables")
        return True
    else:
        print("[WARN] Twilio credentials are not set in environment variables")
        print("Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN")
        return False

def test_imports():
    """Test if WhatsApp-related modules can be imported."""
    try:
        from src.fte.mcp.whatsapp_mcp_server import WhatsAppMCPServer
        print("[OK] WhatsApp MCP Server module can be imported")
    except ImportError as e:
        print(f"[ERROR] WhatsApp MCP Server module import failed: {e}")
        return False

    try:
        from src.fte.watchers.whatsapp_watcher import WhatsAppWatcher
        print("[OK] WhatsApp Watcher module can be imported")
    except ImportError as e:
        print(f"[ERROR] WhatsApp Watcher module import failed: {e}")
        return False

    return True

def main():
    print("WhatsApp Integration Test")
    print("="*30)

    print("\n1. Testing Twilio Installation...")
    twilio_ok = test_twilio_installation()

    print("\n2. Testing Credentials...")
    creds_ok = test_credentials()

    print("\n3. Testing Module Imports...")
    imports_ok = test_imports()

    print("\nSummary:")
    print(f"- Twilio Installation: {'[OK]' if twilio_ok else '[ERROR]'}")
    print(f"- Credentials Set: {'[OK]' if creds_ok else '[ERROR]'}")
    print(f"- Module Imports: {'[OK]' if imports_ok else '[ERROR]'}")

    all_ok = twilio_ok and creds_ok and imports_ok

    print(f"\nOverall Status: {'[SUCCESS] All Good!' if all_ok else '[FAILURE] Issues Found'}")

    if not all_ok:
        print("\nNext Steps:")
        if not twilio_ok:
            print("- Install Twilio: pip install twilio")
        if not creds_ok:
            print("- Set environment variables for Twilio credentials")
        if not imports_ok:
            print("- Check that the source files exist and are accessible")

    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)