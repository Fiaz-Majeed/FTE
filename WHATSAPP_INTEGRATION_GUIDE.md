# Silver Tier WhatsApp Integration Guide

This guide explains how to send WhatsApp messages from your Silver Tier system to your personal WhatsApp.

## Prerequisites

1. **Twilio Account with WhatsApp Sandbox Enabled**
   - Sign up at [Twilio Console](https://console.twilio.com/)
   - Enable WhatsApp Sandbox in your Twilio account
   - Get your Account SID and Auth Token

2. **Environment Variables Setup**
   ```bash
   # Windows
   set TWILIO_ACCOUNT_SID=your_account_sid_here
   set TWILIO_AUTH_TOKEN=your_auth_token_here

   # Linux/Mac
   export TWILIO_ACCOUNT_SID=your_account_sid_here
   export TWILIO_AUTH_TOKEN=your_auth_token_here
   ```

3. **Register Your Phone Number in WhatsApp Sandbox**
   - Go to your Twilio WhatsApp Sandbox settings
   - Join the sandbox by sending "join <keyword>" to the sandbox number
   - Your phone number must be in international format (e.g., +1234567890)

## Method 1: Direct WhatsApp Messaging

Use the simple script to send messages directly:

```bash
python send_to_personal_whatsapp.py
```

## Method 2: MCP Server Integration

Start the WhatsApp-enabled MCP server:

```bash
python -c "from src.fte.mcp.whatsapp_mcp_server import WhatsAppMCPServer; import asyncio; server = WhatsAppMCPServer(); asyncio.run(server.start())"
```

Then use the MCP sender:

```bash
python mcp_whatsapp_sender.py
```

## Method 3: Programmatic Integration

You can also integrate WhatsApp sending into your existing workflows:

```python
from src.fte.mcp.whatsapp_mcp_server import WhatsAppMCPServer
import asyncio

async def send_business_message():
    server = WhatsAppMCPServer()

    # Setup WhatsApp integration
    setup_result = await server.setup_whatsapp_integration({
        'account_sid': 'your_account_sid',
        'auth_token': 'your_auth_token',
        'from_number': 'whatsapp:+14155238886'  # Twilio sandbox number
    })

    if setup_result['status'] == 'success':
        # Send message
        message_result = await server.send_whatsapp_message({
            'to_number': '+1234567890',  # Your phone number
            'message_body': 'Hello from Silver Tier!'
        })

        print(f"Message sent: {message_result}")
```

## Configuration Updates

To enable WhatsApp watching in your config.json, update the Watchers section:

```json
"Watchers": {
  "gmail": {
    "enabled": true,
    "poll_interval": 60
  },
  "whatsapp": {
    "enabled": true,           // Changed from false to true
    "poll_interval": 60
  },
  "linkedin": {
    "enabled": false,
    "poll_interval": 300
  },
  "file_system": {
    "enabled": true,
    "poll_interval": 1
  }
}
```

## Testing Your Setup

1. First, install required dependencies:
   ```bash
   pip install twilio
   ```

2. Set your environment variables as mentioned above

3. Run the test script:
   ```bash
   python send_to_personal_whatsapp.py
   ```

4. Enter your phone number in international format (e.g., +1234567890)

5. Enter your message and send

## Troubleshooting

- **Error: "Phone number must be registered in WhatsApp Sandbox"**
  - Make sure you've joined the WhatsApp Sandbox by sending "join <keyword>" to the Twilio sandbox number

- **Error: "Twilio credentials not provided"**
  - Verify that you've set the environment variables correctly

- **Messages not arriving**
  - Check that your phone number is correctly formatted with the "+" and country code
  - Ensure your Twilio account has sufficient balance for WhatsApp messaging

## Security Note

Keep your Twilio credentials secure and never commit them to version control. Use environment variables as recommended.

## Integration Points

Your Silver Tier system now supports:
- Automated WhatsApp message sending via MCP server
- Business inquiry detection from WhatsApp messages
- Integration with approval workflows
- Scheduling of WhatsApp messages
- Monitoring and logging of WhatsApp communications