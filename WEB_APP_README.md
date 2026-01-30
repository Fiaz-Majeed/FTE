# WhatsApp Web Application - Silver Tier

This is a web-based application that allows you to send WhatsApp messages from any device with a web browser, including mobile devices.

## Prerequisites

1. **Python 3.7 or higher**
2. **Twilio Account** with WhatsApp Sandbox enabled
3. **Environment Variables** set for Twilio credentials

## Setup Instructions

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Twilio Credentials
You need to set the following environment variables:

**On Windows:**
```cmd
set TWILIO_ACCOUNT_SID=your_account_sid
set TWILIO_AUTH_TOKEN=your_auth_token
```

**On Linux/Mac:**
```bash
export TWILIO_ACCOUNT_SID=your_account_sid
export TWILIO_AUTH_TOKEN=your_auth_token
```

### 3. Start the Application
```bash
python start_web_app.py
```

The application will start on `http://localhost:5000`

## Accessing from Mobile Devices

To access the application from a mobile device:

1. Make sure your computer and mobile device are on the same WiFi network
2. Find your computer's IP address:
   - **Windows:** Run `ipconfig` in Command Prompt and look for IPv4 Address
   - **Linux/Mac:** Run `ifconfig` in Terminal and look for inet address
3. On your mobile device, open a web browser and go to:
   `http://YOUR_COMPUTER_IP:5000`

## Features

- **Mobile-Friendly Interface**: Works on smartphones, tablets, and desktops
- **Quick Messages**: One-click buttons for common messages
- **Real-time Status**: Shows message delivery status
- **Secure**: Credentials are stored only on the server, not in the browser

## Troubleshooting

**Cannot connect from mobile device:**
- Ensure both devices are on the same network
- Check firewall settings on your computer
- Verify the IP address is correct

**Twilio credentials not found:**
- Make sure environment variables are set correctly
- Restart the command prompt/terminal after setting variables

**Messages not sending:**
- Verify your phone number is registered in WhatsApp Sandbox
- Check that the number is in international format (+1234567890)

## Security Note

- Keep your Twilio credentials secure
- Only run this application on trusted networks
- Don't expose the application to the public internet without proper security measures