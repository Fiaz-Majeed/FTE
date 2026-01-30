#!/usr/bin/env python3
"""
Flask Web Application for WhatsApp Message Service
This creates a web interface that can be accessed from mobile devices.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from twilio.rest import Client
import threading

app = Flask(__name__)

# Get credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

def send_whatsapp_message(to_number, message_body):
    """
    Send WhatsApp message using Twilio API.

    Args:
        to_number (str): Recipient's phone number in international format
        message_body (str): Message to send

    Returns:
        dict: Result of the operation
    """
    try:
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            return {
                'success': False,
                'error': 'Twilio credentials not found. Please set environment variables.'
            }

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=message_body,
            from_='whatsapp:+14155238886',  # Twilio's WhatsApp Sandbox number
            to=f'whatsapp:{to_number}'
        )

        return {
            'success': True,
            'sid': message.sid,
            'status': message.status,
            'to': to_number,
            'message': message_body,
            'timestamp': str(message.date_sent)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_message():
    """Send WhatsApp message endpoint."""
    data = request.get_json()

    to_number = data.get('to_number', '').strip()
    message_body = data.get('message', '').strip()

    if not to_number or not message_body:
        return jsonify({'success': False, 'error': 'Recipient number and message are required'})

    if not to_number.startswith('+'):
        return jsonify({'success': False, 'error': 'Phone number must start with + followed by country code'})

    # Send message in a separate thread to avoid blocking
    result = send_whatsapp_message(to_number, message_body)
    return jsonify(result)

@app.route('/quick_message', methods=['POST'])
def quick_message():
    """Send predefined quick messages."""
    data = request.get_json()

    to_number = data.get('to_number', '').strip()
    quick_message_type = data.get('type', '').strip()

    # Map quick message types to actual messages
    quick_messages = {
        'hi': 'hi',
        'how_are_you': 'how are you',
        'good_morning': 'Good morning!',
        'thank_you': 'Thank you!'
    }

    if quick_message_type not in quick_messages:
        return jsonify({'success': False, 'error': 'Invalid quick message type'})

    message_body = quick_messages[quick_message_type]

    if not to_number:
        return jsonify({'success': False, 'error': 'Recipient number is required'})

    if not to_number.startswith('+'):
        return jsonify({'success': False, 'error': 'Phone number must start with + followed by country code'})

    result = send_whatsapp_message(to_number, message_body)
    return jsonify(result)

@app.route('/health')
def health_check():
    """Health check endpoint."""
    credentials_set = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)
    return jsonify({
        'status': 'healthy',
        'credentials_set': credentials_set
    })

if __name__ == '__main__':
    # Check if credentials are set
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("Warning: Twilio credentials not found in environment variables.")
        print("Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN before running.")

    app.run(debug=True, host='0.0.0.0', port=5000)